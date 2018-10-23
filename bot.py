#!/usr/bin/env python3
from time import time
from datetime import datetime
import logging
import importlib
from traceback import print_exc
from os import remove

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode

from share.data import owner, token
from share.constants import root_dir

with open(root_dir + 'cache/start.txt') as f:
	start = float(f.read())
	f.close()

def log_time(text):
	print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f] {}'.format(text)))
log_time('imported core libraries')

log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format = log, level=logging.INFO)
logger = logging.getLogger(__name__)

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

updater = Updater(token)
dp = updater.dispatcher
dp.add_error_handler(error)



module_list = [
	'creator',
	#'status',
	'info',
	'commands',
	'text_parse',
	'inline',
	#'buttons',
]

for i in enumerate(module_list):
	# group 0 is taken, so add 1
	group = i[0] + 1
	module = i[1]

	# print group number and module name
	# this seems to be a testing feature
	#print('{}: {}'.format(group, module))

	# use exec to import modules
	exec('import modules.%s' % module)

	# pass dispatcher and group id to the module,
	# so we can implement module reloading later on
	exec('modules.%s.add_handlers(dp, %s)' % (module, group))

	log_time('imported %s.py' % module)



# This doesn't work yet.
'''
def reload_meta(bot, update, args):
	if not args or not update.message.from_user.id == owner:
		return None
	if args[0] in module_list:
		group = [
			i[0] for i in enumerate(module_list)
			if args[0] == i[1]
		# group 0 is taken, so add 1
		][0]+1
		# module_list starts with group 1 at index 0, so subtract 1
		module = module_list[group-1]
		reload_module(bot, update, group, module)

def reload_module(bot, update, group, module):
	reload_message = bot.send_message(
		update.message.chat_id,
		'`Reloading %s.py`' % module,
		parse_mode = ParseMode.MARKDOWN
	)

	# if the module fails to reload, we can't remove its nonexistant group
	try:
		# group 0 is taken, so add 1
		del dp.handlers[group+1]
		dp.groups.remove(group+1)

	except KeyError:
		pass

	try:
		# physically reload the module in memory
		print('importlib.reload(modules.%s)' % module)
		exec('importlib.reload(modules.%s)' % module)
		# re-execute the add_handlers() function
		print('modules.%s.add_handlers(dp, %s)' % (module, group))
		exec('modules.%s.add_handlers(dp, %s)' % (module, group))

		# update the message
		bot.edit_message_text(
			chat_id = update.message.chat_id,
			message_id = reload_message.message_id,
			text = '`Reloaded %s.py`' % module,
			parse_mode = ParseMode.MARKDOWN
		)

	except:
		# print errors if they occur
		print_exc()

		# update the message
		bot.edit_message_text(
			chat_id = update.message.chat_id,
			message_id = reload_message.message_id,
			text = '`Failed to reload %s.py`' % module,
			parse_mode = ParseMode.MARKDOWN
		)

dp.add_handler(CommandHandler('reload', reload_meta, pass_args = True))
log_time('activated reloader.py')
'''



# clean start.txt from the cache
remove(root_dir + 'cache/start.txt')
try:
	remove(root_dir + 'cache/reboot.txt')
except FileNotFoundError:
	pass

# debug
#exit()

# start the bot
updater.start_polling(clean = True)
updater.idle()
