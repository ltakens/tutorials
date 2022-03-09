'''
Outline of a script that takes a screenshot of a webpage and sends it
to a Telegram group.

Example:
    python app.py https://www.google.com
'''
from urllib.parse import quote_plus
import io
import re
import sys

from PIL import Image
import requests

try:
    from settings import TELEGRAM_BOT, TELEGRAM_CHAT_ID
except ModuleNotFoundError:
    sys.stdout.write(
        'Create a file called settings.py and save these settings'
        'in it:\r\n\r\nTELEGRAM_BOT=...\r\nTELEGRAM_CHAT_ID=...\r\n'
        '\r\nThen run the script again.'
    )
    sys.exit(1)


RED   = "\033[1;31m"
RESET = "\033[0;0m"
TELEGRAM_MESSAGE = 'Hello Telegram, look at this screenshot of %s.'


def print_error_message(error_message):
    sys.stdout.write(f'{RED}{error_message}{RESET}\r\n')


def send_telegram_message(text):
    api_url = f'https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage?' \
        f'chat_id={TELEGRAM_CHAT_ID}&text=' + quote_plus(text, safe='')
    try:
        result = requests.get(api_url, timeout=1)
        if not result.status_code == 200:
            raise Exception(f'{result.status_code} {result.text}')
        return True
    except Exception as e:
        print_error_message(f'Failed to send Telegram message: {str(e)}')


def send_image_to_telegram(image_bytes):
    api_url = f'https://api.telegram.org/bot{TELEGRAM_BOT}/sendPhoto?chat_id=' + \
        str(TELEGRAM_CHAT_ID)
    try:
        result = requests.post(api_url, files={ 'photo': image_bytes }, timeout=10)
        if not result.status_code == 200:
            raise Exception(f'{result.status_code} {result.text}')
        file_id = result.json()['result']['photo'][0]['file_id']
        return file_id
    except Exception as e:
        print_error_message(f'Failed to upload image to Telegram: {str(e)}')
    

def take_screenshot(url):
    # TODO: Render url in headless browser and take screenshot 
    # Fake placeholder image for now
    img  = Image.new(mode = "RGB", size = (100, 100), color = (209, 123, 193))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='png')
    return img_bytes.getvalue()


def parse_arguments():
    if len(sys.argv) == 2:
        url = sys.argv[1]
        if re.match(r'^https?:\/\/', url):
            return url
        print_error_message('Please provide a full URL, like https://www.google.com.')
        sys.exit(1)

    print_error_message('Please provide the website URL when invoking the script, '
                        f'.e.g.: `python app.py https://www.mywebsite.com`')
    sys.exit(1)


def main():
    # Get URL inputed by user on invoking the script
    url = parse_arguments()
    
    # Take screenshot
    screenshot = take_screenshot(url)

    # Send screenshot to Telegram
    send_image_to_telegram(screenshot)

    # Send text message to Telegram group
    if send_telegram_message(TELEGRAM_MESSAGE % url):
        sys.stdout.write('OK\r\n')


if __name__ == '__main__':
    main()
