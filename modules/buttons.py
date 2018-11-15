#!/usr/bin/env python3
from os.path import dirname
from time import sleep

from telegram import ParseMode
from telegram import InlineKeyboardButton as IKButton
from telegram import InlineKeyboardMarkup as IKMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from bin.background import background
from share.constants import root_dir

path = root_dir + 'share/'
with open(path + 'roflcopter1.txt') as f:
	rofl_1 = f.read()
with open(path + 'roflcopter2.txt') as f:
	rofl_2 = f.read()
with open(path + 'roflcopter.txt') as f:
	rofl_x = f.read()

rofl_list = [
	'```\n%s\n```' % i for i in
	[rofl_1, rofl_2, rofl_x]
]

def land_rofl(bot, chat_data, chat_id, message_id):
	if message_id in chat_data and chat_data[message_id] == 'rofl_land':
		# begin landing
		chat_data.pop(message_id)
		bot.edit_message_text(
			chat_id = chat_id,
			message_id = message_id,
			text = rofl_list[2],
			parse_mode = ParseMode.MARKDOWN,
			reply_markup = IKMarkup([[
				IKButton(
					'Emergency landing...',
					callback_data = 'rofl_landing',
				),
			]]),
		)
		sleep(1)

	# complete landing
	chat_data[message_id] = 'rofl_landing'
	bot.edit_message_text(
		chat_id = chat_id,
		message_id = message_id,
		text = rofl_list[2],
		parse_mode = ParseMode.MARKDOWN,
		reply_markup = IKMarkup([[
			IKButton(
				'Fly again!',
				callback_data = 'rofl_fly %s %s' % (chat_id, message_id)
			),
			IKButton(
				'Stop flying.',
				callback_data = 'rofl_stop',
			),
		]])
	)

def fly_rofl(bot, chat_data, chat_id, message_id):
	message_id = int(message_id)
	if int(chat_id) > 0:
		delay = .1
		count = 30
	else:
		delay = 1
		count = 10
	# delay after initial frame
	sleep(delay)
	for i in range(count):
		# if rofl_land has been called, stop
		if message_id in chat_data and chat_data[message_id] == 'rofl_land':
			land_rofl(bot, chat_data, chat_id, message_id)
			break
		bot.edit_message_text(
			chat_id = chat_id,
			message_id = message_id,
			text = rofl_list[i % 2],
			parse_mode = ParseMode.MARKDOWN,
			reply_markup = IKMarkup([[
				IKButton(
					'Flying...',
					callback_data = 'rofl_land',
				),
			]]),
		)
		sleep(delay)
	if message_id in chat_data and chat_data[message_id] == 'rofl_land':
		land_rofl(bot, chat_data, chat_id, message_id)
		return None
	land_rofl(bot, chat_data, chat_id, message_id)

@background
def start_rofl(bot, update, chat_data):
	sent = bot.send_message(
		text = rofl_list[2],
		chat_id = update.message.chat_id,
		parse_mode = ParseMode.MARKDOWN,
		reply_markup = IKMarkup([[
			IKButton(
				'Preparing for flight...',
				callback_data = 'rofl_land',
			),
		]])
	)
	fly_rofl(bot, chat_data, sent.chat_id, sent.message_id)

@background
def rofl_button(bot, update, chat_data):
	query = update.callback_query
	bot.answer_callback_query(query.id)
	chat_id = query.message.chat_id
	message_id= query.message.message_id

#	if query.data == 'delete':
#		bot.delete_message(
#			chat_id = chat_id,
#			message_id = message_id,
#		)
#		return None
	if False:
		pass

	elif query.data.startswith('rofl_fly '):
		chat_id, message_id = query.data.split()[1:]
		fly_rofl(bot, chat_data, chat_id, message_id)
		return None

	elif query.data == 'rofl_landing':
		sleep(3)
		if message_id in chat_data and chat_data[message_id] == 'rofl_landing':
			chat_data.pop(message_id)
		else:
			land_rofl(bot, chat_data, chat_id, message_id)

	elif query.data == 'rofl_land':
		chat_data[message_id] = 'rofl_land'
		sleep(3)
		if message_id in chat_data and chat_data[message_id] == 'rofl_land':
			land_rofl(bot, chat_data, chat_id, message_id)

	elif query.data == 'rofl_stop' or query.data == 'rofl_null':
		bot.edit_message_text(
			chat_id = chat_id,
			message_id = message_id,
			text = rofl_list[2],
			parse_mode = ParseMode.MARKDOWN,
			reply_markup = IKMarkup([[
			]]),
		)

	else:
		pass

def add_handlers(dp, group):
	for i in [
		CommandHandler('rofl', start_rofl, pass_chat_data = True),
		CallbackQueryHandler(rofl_button, pattern = 'rofl', pass_chat_data = True)
	]: dp.add_handler(i, group)
