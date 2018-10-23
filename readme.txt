Dependencies:
apt:
	python3
pip3:
	python-telegram-bot
	psutil

The only file you should need to create in order to run this bot is the following:

share/data.py:
#!/usr/bin/env python3
owner = '<Your Telegram user ID>'
token = '<Your bot's Telegram user ID>'
