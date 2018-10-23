#!/usr/bin/env python3
from multiprocessing import Process, Queue
from resource import RLIMIT_CPU, getrlimit, setrlimit
from queue import Empty
from re import match

from telegram.constants import MAX_MESSAGE_LENGTH
from telegram.ext import CommandHandler

from bin.background import background

def start(bot, update):
	bot.send_message(update.message.chat.id, 'Started!')

def identify(bot, update):
	bot.send_message(update.message.chat.id,
		'I\'m here!'
	)

@background
def calc(bot, update, args):
	expression = ''.join(args)

	def calc_reader(expression):
		queue = Queue(1)
		def calc_sandbox(expression, queue):
			def calc_limit(expression, queue):
				rsrc = RLIMIT_CPU
				soft, hard = getrlimit(rsrc)
				setrlimit(rsrc, (1, hard))
				queue.put(str(eval(expression)))
			p = Process(target = calc_limit, args = [expression, queue])
			p.start()
		calc_sandbox(expression, queue)
		try:
			value = queue.get(timeout = 1)
		except Empty:
			value = 'Calculation timed out.'
		return value

	if match('^[0-9.()*/+-]+$', expression):
		resp = calc_reader(expression)
		if len(resp) > MAX_MESSAGE_LENGTH:
			resp = 'The value is too long.'
	else:
		resp = 'Only the characters `0-9.()*/+-` are permitted.'
	bot.send_message(update.message.chat.id,
		resp,
	)

def echo(bot, update, args):
	try:
		reply = update.message.reply_to_message.message_id
	except:
		reply = False
	empty = not args

	# why did I put chat_title and chat.id in the str.format()?
	# I have no idea, but I don't want it there
	if empty and reply:
		# forward message
		bot.forward_message(
			chat_id = update.message.chat.id,
			from_chat_id = update.message.chat.id,
			message_id = update.message.reply_to_message.message_id
		)
	elif not empty and reply:
		# echo with reply
		bot.send_message(update.message.chat.id,
			' '.join(args).format(
				#chat_title = update.message.chat.title,
				#chat_id = update.message.chat.id,
				nl = '\n'
			),
			reply_to_message_id = reply
		)
	elif not empty and not reply:
		# echo
		bot.send_message(update.message.chat.id,
			' '.join(args).format(
				#chat_title = update.message.chat.title,
				#chat_id = update.message.chat.id,
				nl = '\n'
			)
		)
	elif empty and not reply:
		bot.send_message(update.message.chat.id,
			'You can make me repeat things with this command.'
			+ 'Also, {nl} will be replaced with a newline.'
		)

def github_link(bot, update):
	bot.send_photo(
		chat_id = update.message.chat.id,
		photo = 'AgADAwADs6cxG7F2IU5xnR7ZCnfs6VEHhzEABKIU0x2zu1zMa4oBAAEC',
		caption = 'https://github.com/nejni-marji/Nenmaj_Bot_v3',
	)

def add_handlers(dp, group):
	for i in [
		CommandHandler('start', start),
		CommandHandler('relmaj', identify),
		CommandHandler('nenmaj', identify),
		CommandHandler('calc', calc, pass_args = True),
		CommandHandler('echo', echo, pass_args = True),
		CommandHandler('github', github_link),
		CommandHandler('foss', github_link),
	]: dp.add_handler(i, group)
