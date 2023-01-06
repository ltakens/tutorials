"""Scrape Shopify domains from a database website using Google reCAPTCHA.

This script scrapes `Myip.ms`_ for Shopify owned domains.
This script scrapes synchronously, with additional delays so as not to
burden the service.
This script uses `Anti-Captcha`_ to solve Google reCAPTCHA.
This script uses public proxies to circumvent IP based request limiting.

Warning
-------
Don't scrape any resources unless you have permission to do so.

Notes
-----
1. Register with Anti-Captcha to get an API key.
   See https://anti-captcha.com/clients/entrance/register
2. Optionally create a virtual Python environment.
   See https://docs.python-guide.org/dev/virtualenvs/.
3. Save this script to a file called ``script.py``.
4. In the same directory create a file called ``https_proxies.txt`` and save
   proxies to use in them, one on each line. See the
   :func:`read_proxies_from_file` function for a formatting example.
5. Run the script as below. Assuming this script is saved as ``script.py``:

    $ ANTI_CAPTCHA_KEY=secret123 python3 script.py

6. View scraped domains in ``results/found_domains.txt``.

.. _Myip.ms: https://myip.ms
.. _Anti-Captcha: https://anti-captcha.com/
"""

__author__ = 'Public Apps'
__contact__ = "code@public-apps.com"
__copyright__ = 'Copyright (C) 2023 Public Apps'
__version__ = '0.0.1'

import json
import os
import random
import re
import time
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup


# Script constants
# We scrape 23.227.38.32 in this example, but Shopify also uses other IP's
DOMAIN_LISTING_URL_TEMPLATE = \
    'https://myip.ms/browse/sites/{page}/' \
    'ipID/23.227.38.32/ipIDii/23.227.38.32'
IP_API_URL = 'https://public-apps.com/what-is-my-ip/txt/'
RECAPTCHA_REGEX = r"grecaptcha.execute\('([^']{10,})'," \
    r"\s+{\s+action\:\s+'(\w+)'\s+}"
START_PAGE = 1  # set this to 1 if first starting
PROXIES_FILE = 'free_https_proxies.txt'
RESULTS_FILE = 'results/found_domains.txt'
REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
        'image/avif,image/webp,image/apng,*/*;q=0.8,'
        'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 '
        'Safari/537.36',
}
MAX_REQUESTS_PER_IP = 20
TIMEOUT = 120  # default timeout for requests (proxies can be very slow)

# Read the Anti-Captcha key from environmental files
# Read it on script startup, so a KeyError's is raised before we are scraping
ANTI_CAPTCHA_KEY = os.environ['ANTI_CAPTCHA_KEY']

# Keep track of performing proxies and print to stdout on exit
good_proxies = []
bad_proxies = []
domains = set()


class Fetcher:
    """Wrapper to `requests`, handling cookies and exceptions.

    Parameters
    ----------
    proxy : str, optional
        Proxy to use for all the requests of this Fetcher
    cookies : dict, optional
        Cookies object that gets updates for every 200 response
    timeout : int, optional
        Timeout to set on all requests of this Fetcher

    Attributes
    -------
    proxy : str
        Proxy to use for all the requests of this Fetcher
    cookies : dict
        Cookies object that gets updates for every 200 response
    timeout : int
        Timeout to set on all requests of this Fetcher

    Examples
    --------
    >>> fetcher = Fetcher(proxy='123.1.2.44:8080')
    >>> fetcher.post('https://some-site.com/login', {'login': 'hello123'})
    >>> fetcher.get('https://some-site.com/my-account')
    """
    def __init__(self, proxy: str = None, cookies: Dict = None,
                 timeout: int = TIMEOUT):
        self.proxy = proxy
        self.cookies = cookies or {}
        self.timeout = timeout

    def _request(self, url: str, method: str = 'GET', data=None,
                _headers=None) -> Optional[requests.Response]:
        # Prints e.g. "GET https://some-url, proxy: 123.1.2.44:8080, data"
        print(
            f'{method.upper()} {url}, '
            f'proxy: {self.proxy}, '
            f'data: {data and json.dumps(data) or "-"}, '
            f'cookies: {self.cookies}'
        )

        # Get requests.get or requests.post function
        func = getattr(requests, method.lower())

        # Override or add headers for individual requests
        headers = {**REQUEST_HEADERS, **(_headers or {})}

        # Determine the `proxies` kwarg to pass to the request function
        proxies = self.proxy and {'http': self.proxy, 'https': self.proxy}

        # perform request and catch errors
        try:
            res = func(url, data=data, headers=headers, cookies=self.cookies,
                       proxies=proxies, timeout=self.timeout)

            if res.status_code == 200:
                # if we used requests.Session, cookies would be updated
                # automatically and HTTP connections would potentially be
                # reused
                new_cookies = res.cookies.get_dict()
                print(f'HTTP 200, so updating cookies with: {new_cookies}')
                self.cookies.update(new_cookies)

                return res

            raise Exception(f'Response status was {res.status_code}')
        except Exception as e:
            print(f'Exception during requesting {url}: {e}')

    def post(self, url: str, data: Dict) -> Optional[requests.Response]:
        """Perform a POST request."""
        return self._request(url, method='post', data=data, _headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'myip.ms',
            'Origin': 'myip.ms',
            'Referer': url,
        })

    def get(self, url: str) -> Optional[requests.Response]:
        """Perform a GET request."""
        return self._request(url)


def read_proxies_from_file() -> List[str]:
    """Return proxies from a text file configured in ``PROXIES_FILE``.

    File is expected to have one ``host:port`` per line.
    E.g.:

    1.2.3.4:8080
    2.3.4.5:999
    3.4.5.6:9090
    """
    with open(PROXIES_FILE, 'r') as fin:
        proxies = [x.strip('\n') for x in fin.readlines()]
        return proxies


def ensure_directories(file_path: str) -> None:
    """Make directories found in file path."""
    if '/' in file_path:
        dirs_path = '/'.join(file_path.split('/')[:-1])
        if not os.path.isdir(dirs_path):
            os.makedirs(dirs_path)


def write_domains_to_file(domains: Iterable[str]) -> None:
    """Write gathered domain names to an output file."""
    ensure_directories(RESULTS_FILE)
    with open(RESULTS_FILE, 'a') as fout:
        for domain in domains:
            fout.write(f'{domain}\n')


def proxy_is_working(proxy: str) -> bool:
    """Test whether we can communicate using the proxy."""
    fetcher = Fetcher(proxy)
    res = fetcher.get(IP_API_URL)
    if res:
        ip = res.text
        print(f'{IP_API_URL} says our IP is {ip}.')

        # Check whether the API reports the IP address that is
        # in the proxy string. Some proxies show another IP than the one
        # that we connect to.
        if ip in proxy:
            print('This is our proxy\'s IP.')
            good_proxies.append(proxy)
            return True

        print('This is NOT our proxy\'s IP.')
    else:
        print(f'Did not get a response from the proxy.')
        bad_proxies.append(proxy)

    return False


def pick_proxy() -> Iterator[str]:
    """Yield random proxies one by one."""
    proxies = read_proxies_from_file()
    while proxies:
        # Pick random proxy
        index = random.choice(range(len(proxies)))

        # Make sure proxy isn't picked twice
        proxy = proxies.pop(index)

        print(f'Picking proxy {proxy}. {len(proxies)} proxies left.')
        yield proxy


def _create_anti_captcha_task(
    url: str,
    site_key: str,
    action: str
) -> Optional[int]:
    task_data = {
        "clientKey": ANTI_CAPTCHA_KEY,
        "task": {
            "type":"RecaptchaV3TaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key,
            "minScore": 0.3,
            "pageAction": action,
            "isEnterprise": False,
        },
        "softId": 0
    }
    res = requests.post('https://api.anti-captcha.com/createTask',
                        json=task_data)
    print(res.text)

    # Handle errors
    if res.status_code != 200:
        print('Failed to create Anti-Captcha task (res status: '
              f'{res.status_code}).')
        return

    data = res.json()
    task_id = data.get('taskId')
    return task_id


def _get_anti_captcha_solution(task_id: int) -> Optional[str]:
    """Query Anti-Captcha service for solution to previously created task."""
    # Data to send
    task_data = {
        "clientKey": ANTI_CAPTCHA_KEY,
        "taskId": task_id,
    }

    # Query
    res = requests.post('https://api.anti-captcha.com/getTaskResult',
                        json=task_data)
    if res.status_code != 200:
        print(f'Could not get recaptcha response: status ${res.status_code}.')
        return

    # Parse result
    try:
        # Expected: {
        #   "errorId": 0,
        #   "status": "ready",
        #   "solution": {
        #     "gRecaptchaResponse": "032SDF..."
        #   },
        #   "cost": "0.00100",
        #   "ip": "2a02:a212:41:de01:813e:162f:4cc7:4812",
        #   "createTime": 1671125904,
        #   "endTime": 1671125915,
        #   "solveCount": 0
        # }
        return res.json()['solution']['gRecaptchaResponse']
    except KeyError:
        print(f'Unexpected data instead of Anti-Captcha solution.')
        print(res.text)


def solve_recaptcha(url: str, old_html: str) -> Optional[Tuple[str, str]]:
    """Refetch the page after solving recaptcha and return new HTML.

    Returns
    -------
    tuple
        Recaptcha solution and captcha token if recaptcha was solved.
    None
        if recaptcha could not be solved.
    """
    match = re.search(RECAPTCHA_REGEX, old_html)
    if not match:
        print('Recaptcha key/action not found on page')
        return
    site_key = match.group(1)
    action = match.group(2)

    # Create Anti-Captcha task and get taskId
    task_id = _create_anti_captcha_task(url, site_key, action)
    if not task_id:
        print('Did not get a taskId from Anti-captcha. Not solving recaptcha.')
        return

    solution = None
    times_waited = 0
    while not solution and times_waited < 3:
        time.sleep(6)
        solution = _get_anti_captcha_solution(task_id)

    if not solution:
        print('Anti-captcha task could not be solved.')
        return
    print(f'We got a solution from Anti-Captcha: {solution}')

    # Get captcha token needed later
    parsed = BeautifulSoup(old_html, 'html.parser')
    input_elem = parsed.find('input', attrs={'name': 'captcha_token'})
    token = input_elem.get('value')

    return solution, token


def has_next_page(parsed_html: BeautifulSoup) -> Optional[bool]:
    """Return whether there are more pages in the current listing.

    Returns
    -------
    bool
        Whether there are more pages
    None
        If result set info not found

    Note
    ----
    Pagination visible in the browser is not present in the server side
    rendered HMTL. Use result set info instead. Expecting the result set
    info to look like:

    .. code-block:: html

        <div align="right" class="right nowrap arial11">
            <b class="sites_tbl_start">1,601</b> -
            <b class="sites_tbl_end">1,650</b> &nbsp;of&nbsp;
            <b>217,793</b> records &nbsp;
        </div>

    """
    cur_results_end = parsed_html.find(attrs={'class': 'sites_tbl_end'})
    if cur_results_end:
        tot_results = cur_results_end.find_next_sibling('b')
        if tot_results:
            clean = lambda x: re.sub(r'[,\.]', '', x)
            cur_results_end_int = int(clean(cur_results_end.text))
            tot_results_int = int(clean(tot_results.text))
            print(f'This page is showing results {cur_results_end_int} / '
                  f'{tot_results_int}.')
            return cur_results_end_int < tot_results_int


def post_solution_and_update_cookies(url: str, token: str, solution: str,
                                     fetcher: Fetcher) -> bool:
    """Post recaptcha solution to website again to get cookies to proceed.

    Returns
    -------
    bool
        Whether the website responded with HTTP 200 and we assume the website
        accepted the recaptcha solution
    """
    data = {
        'g_recaptcha_loaded': 'yes',
        'captcha_token': token,
        'g_recaptcha_response': solution,
    }
    res = fetcher.post(url, data)
    if not res:
        print(f'Anti-Captcha was not accepted.')
        return False

    # On success we have the 's2_uGoo' cookie, and the response body is
    # '<script>window.location=window.location.href.split("#")[0];</script>'
    if res.text in (
        '<script>window.location=window.location.href.split("#")[0];</script>',
    ) and 's2_uGoo' in fetcher.cookies.keys():
        return True

    print('Unexpected response to submission of reCAPTCHA solution...')
    return False


def page_has_recaptcha(html: str) -> bool:
    """Return whether the html contains the known recaptcha markup."""
    html_lower = html.lower()
    return 'human verification' in html_lower or 'human being' in html_lower


def do_some_work_until_finished_or_proxy_dead(proxy: str, page: int) -> int:
    # Verify the proxy is working
    if not proxy_is_working(proxy):
        # Return the current page for scraping using another proxy
        return page

    # Keep track of number of requests we did on this proxy
    num_requests = 0
    # Keep track of the page we're scraping
    page_next_up = page
    # Scrape using a fetcher obj that remembers cookies and catches exceptions
    fetcher = Fetcher(proxy)
    while num_requests < MAX_REQUESTS_PER_IP:
        url = DOMAIN_LISTING_URL_TEMPLATE.format(page=page_next_up)
        res = fetcher.get(url)
        num_requests += 1
        if not res:
            print(f'No content for {url}. Returning for another proxy.')
            return page_next_up

        # Check the page for recaptcha
        html = res.text
        if page_has_recaptcha(html):
            # We've got reCAPTCHA
            print('We received a reCAPTCHA....')
            # Get the solution
            solved = solve_recaptcha(url, html)
            if not solved:
                print('Did not get solution, returning for another proxy.')
                return page_next_up
            solution, token = solved

            # Post the solution and get new cookies
            if not post_solution_and_update_cookies(url, token, solution,
                                                    fetcher):
                print('ReCAPTCHA solution was not accepted, returning for '
                      'another proxy.')
                return page_next_up

            # Now we should be able to get the original url using the same
            # fetcher that has the updated cookies
            res = fetcher.get(url)
            num_requests += 1

            # If the new attempt after captcha failed, give up
            if not res:
                print('Failed to refetch. Returning for '
                      'another proxy.')
                return page_next_up

            # If there's still a recaptcha, give up
            if page_has_recaptcha(res.text):
                print('Refetched, but another reCAPTCHA. Returning for '
                      'another proxy.')
                return page_next_up

            # Looks like we solved the captcha
            print('Looks like we solved the recaptcha. Continuing to parse.')
            html = res.text

        print('Parsing the page....')
        parsed = BeautifulSoup(html, 'html.parser')

        table = parsed.find('table', attrs={'id': 'sites_tbl'})
        if not table:
            print('Table with domains not found. Giving up.')
            # When we hit the rate limit (maybe proxy was used before),
            # we get redirected to https://myip.ms/info/limitexcess, so res.url
            # tells us the reason the table is not found.
            print(f'res.url was: {res.url}')
            print(f'res.text[250] was: {res.text[:250]}')
            return page_next_up

        cells = table.find_all('td', attrs={'class': 'row_name'})
        domains_ = set([c.text.strip() for c in cells])
        domains.update(domains_)
        print(f'Added {len(domains_)} domains: {domains_}')
        write_domains_to_file(domains_)
        time.sleep(5)

        # Go for next page, if there is one
        more_pages = has_next_page(parsed)
        if more_pages is None:
            # Next page couldn't be determined
            print(f'Couldn\'t determine whether there are more pages to '
                  f'scrape. Returning no next page.')
            return None
        elif more_pages:
            # Go on to the next page
            page_next_up += 1
        else:
            # All done
            return None

        print('\n')

    # When done with the 20, return the next page that should be scraped
    return page_next_up


def main():
    page = START_PAGE
    # Keep picking proxies and try to scrape using them
    for proxy in pick_proxy():
        page = do_some_work_until_finished_or_proxy_dead(proxy, page)
        if not page:
            print('No more pages. Done.')
            break

        print(f'Next up is page {page}.')
        time.sleep(3)  # delay
        print('\n\n')
    else:
        print(f'No more proxies. Quitting at page {page}.')


if __name__ == '__main__':
    try:
        main()
    finally:
        print(f'good_proxies: {good_proxies}')
        print(f'bad_proxies: {bad_proxies}')
        print(f'domains: {domains}')
