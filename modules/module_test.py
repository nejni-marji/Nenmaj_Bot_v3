#!/usr/bin/env python3
from pprint import pprint
#from telegram import ParseMode
from telegram.ext import CommandHandler


def run_test(bot, update, args):
	pprint(bot)
	pprint(update)
	pprint(args)

def add_handlers(dp, group):
	for i in [
		CommandHandler('test', run_test, pass_args = True),
	]: dp.add_handler(i, group = group)
