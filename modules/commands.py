#!/usr/bin/env python3
from multiprocessing import Process, Queue
from resource import RLIMIT_CPU, getrlimit, setrlimit
from queue import Empty
from re import match
from random import choice

from telegram.constants import MAX_MESSAGE_LENGTH
from telegram.ext import CommandHandler

from bin.background import background
from bin.rhymes import get_www_rhymes

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


NO_RHYMES = [':(', ':\'(', 'ono', 'OnO', 'TnT', 'orz']

@background
def tg_rhyme(bot, update, args):
	if not args:
		return None

	print('{} ({}) asked for rhymes.'.format(
		update.message.from_user.first_name,
		update.message.from_user.id,
	))
	print('Processing to obtain rhymes for: %s' % ' '.join(args))

	def get_clean_rhyme_list(query):
		print('Getting rhymes for: %s' % query)
		to_clean = get_www_rhymes(query)
		if not to_clean:
			return NO_RHYMES
		else:
			return to_clean

	queries = [arg.rstrip(',').lstrip('@') for arg in args]
	if False and len(queries) > 10:
		resp = "That's just too many words, dude. (Max: 10)"
	else:
		clean_lists = [get_clean_rhyme_list(query) for query in queries]
		rhymes = [choice(clean_list) for clean_list in clean_lists]
		resp = ', '.join(rhymes)

	bot.send_message(update.message.chat.id,
		resp,
		reply_to_message_id = update.message.message_id
	)

@background
def tg_rhyme_all(bot, update, args):
	if not args:
		return None

	print('Processing to obtain ALL rhymes for: %s' % ' '.join(args))
	rhymes = get_www_rhymes(args[0])
	resp = ', '.join(rhymes)
	if not resp:
		resp = choice(NO_RHYMES)

	bot.send_message(update.message.chat.id,
		resp,
		reply_to_message_id = update.message.message_id
	)

def add_handlers(dp, group):
	for i in [
		CommandHandler('rhyme', tg_rhyme, pass_args = True),
		CommandHandler('rhymes', tg_rhyme, pass_args = True),
		CommandHandler('rhymeall', tg_rhyme_all, pass_args = True),
		CommandHandler('start', start),
		CommandHandler('relmaj', identify),
		CommandHandler('nenmaj', identify),
		CommandHandler('calc', calc, pass_args = True),
		CommandHandler('echo', echo, pass_args = True),
		CommandHandler('github', github_link),
		CommandHandler('foss', github_link),
	]: dp.add_handler(i, group)
