# Telegram script

Outline of a script that takes a screenshot of a webpage and sends it
to a Telegram group.

## Requirements
You need to have [virtualenv](https://virtualenv.pypa.io/en/latest/) and [Python 3](https://www.python.org/downloads/) installed and available on the command line as a `virtualenv` and `python3` executable or alias.

## Preparation
[Create a Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot) and [a chat](https://telegram.org/faq#q-how-do-i-create-a-group). Enter the details in your shell.

```
# Append the bot token after the = sign
BOT=
# Append the chat id after the = sign
CHAT=
```

## Running the script
Run the following commands to install and run the Python script

```
# Install
git clone https://github.com/ltakens/tutorials.git
cd tutorials/python/telegram
virtualenv .env -p python3
source .env/bin/activate
pip3 install -r requirements.txt
cat <<EOF >> settings.py
TELEGRAM_BOT="$BOT"
TELEGRAM_CHAT_ID="$CHAT"
EOF

# Run
python app.py https://public-apps.com
```
