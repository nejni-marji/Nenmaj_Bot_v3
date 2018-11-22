#!/usr/bin/env python3
import re
from uuid import uuid4
from collections import OrderedDict

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import ParseMode
from telegram.ext import InlineQueryHandler, CommandHandler
from telegram.error import BadRequest

from bin.background import background
from share.constants import fullwidth

subs_dict = OrderedDict([
	('shrug', '¯\_(ツ)_/¯'),
	('lenny', '( ͡° ͜ʖ ͡°)'),
	('cccp', '☭'),
	('ib', '‽'),
	('fake_cmd', '/\xad'),
	('long_jbo', 'jbojevysofkemsuzgugje\'ake\'eborkemfaipaltrusi\'oke\'ekemgubyseltru'),
])

subs_text = '\n'.join([
	'{{{}}}: {}'.format(
		i, subs_dict[i]
	)
	for i in subs_dict
])

def manip_strike(to_repl):
	repl = '\u0336'.join(list(to_repl)) + '\u0336'
	return repl

def manip_under(to_repl):
	repl = '\u0332'.join(list(to_repl)) + '\u0332'
	return repl

def manip_vapor(to_repl):
	repl = ''
	for i in list(to_repl):
		if i == ' ':
			repl += '    '
		elif i not in fullwidth:
			repl += i
		else:
			repl += chr(0xFEE0 + ord(i))
	return repl

manips = {
	's': manip_strike,
	'u': manip_under,
	'v': manip_vapor,
}

manip_demos = {
	's': 'S̶t̶r̶i̶k̶e̶t̶h̶r̶o̶u̶g̶h̶',
	'v': 'Ｖａｐｏｒｗａｖｅ',
	'u': 'U̲n̲d̲e̲r̲l̲i̲n̲e̲',
}

re_manips = re.compile('<([%s])>.*?</\\1>' % ''.join(list(manips)))

def manip_manips(query):
	if not '<' in query:
		return query

	match = re_manips.search(query)
	if not match:
		return query

	manip = manips[match.group(1)]
	return manip_manips(
		query.replace(match.group(),
		manip(match.group()[3:-4]))
	)

help_text = [
	'If you\'ve never used an inline bot before, [click here!](https://telegram.org/blog/inline-bots)"',
	'Otherwise, read on.',
	'',
	'You can use Telegram\'s native HTML tags:',
	'<b>, <i>, <a>, <code>, <pre>',
	'If you use <a>, you should get an option to disable web preview.',
	'',
	'You can also use my custom HTML tags:',
	'%s: <s>' % manip_demos['s'],
	'%s: <v>' % manip_demos['v'],
	'%s: <u>' % manip_demos['u'],
	'',
	'The bot can replace certain values delimited with braces',
	'Click on \'Replacements\' in inline mode to see the full list.',
	'',
	'The bot should automatically determine what modes to enable based on your query.',
]

@background
def inlinequery(bot, update):
	inline_query = update.inline_query
	query = update.inline_query.query
	user = update.inline_query.from_user
	print('InlineQuery from {} ({}):\n"{}"'.format(
		user.first_name, user.id, query
	))

	try:
		query = query.format(**subs_dict)
	except:
		pass

	if update.inline_query.query == query:
		subbed = False
	else:
		subbed = True

	def inline_subs(r):
		if subbed:
			text = query
			desc = text
		else:
			text = subs_text
			desc = 'Click here to see replacements.'
		r.append(InlineQueryResultArticle(id=uuid4(),
			title = 'Replacements',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
			)
		))

	def inline_help(r):
		text = '\n'.join(help_text)
		desc = 'Don\'t know how this works? Click here!'
		r.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Help and Usage',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.MARKDOWN,
				disable_web_page_preview = True
			)
		))

	def inline_error(r):
		text = 'This message should not appear.'
		desc = text
		r.append(InlineQueryResultArticle(id=uuid4(),
			title = 'Error',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.HTML,
			)
		))

	def inline_html(r):
		if not ('<' in query and '>' in query):
			return None
		text = query
		desc = text
		r.append(InlineQueryResultArticle(id=uuid4(),
			title = 'HTML',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.HTML,
				disable_web_page_preview = False
			)
		))

	def inline_html_noprev(r):
		if not ('<a href' in query and '</a>' in query):
			return None
		text = query
		desc = text
		r.append(InlineQueryResultArticle(id=uuid4(),
			title = 'HTML (No Preview)',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.HTML,
				disable_web_page_preview = True
			)
		))

	def inline_manips(r):
		if not ('<' in query and '>' in query):
			return None
		text = manip_manips(query)
		if text == query:
			return None
		desc = text
		r.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Manips',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.HTML
			)
		))

	def inline_manips_noprev(r):
		if not ('<a href' in query and '</a>' in query):
			return None
		if not ('<' in query and '>' in query):
			return None
		text = manip_manips(query)
		if text == query:
			return None
		desc = text
		r.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Manips (No Preview)',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.HTML,
				disable_web_page_preview = True
			)
		))

	def inline_strike(r):
		text = manip_strike(query)
		desc = text
		r.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Strikethrough',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
			)
		))

	def inline_under(r):
		text = manip_under(query)
		desc = text
		r.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Underline',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
			)
		))

	def inline_vapor(r):
		text = manip_vapor(query)
		desc = text
		r.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Vaporwave',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
			)
		))

	def clean_results(n = 0):
		if n >= 3:
			raise RecursionError('clean_results() reached n=%d' % n)
		r = []
		inline_help(r)
		inline_subs(r)
		if query and n <= 2:
			if n <= 0:
				inline_html(r)
				inline_html_noprev(r)
			if n <= 1:
				inline_manips(r)
				inline_manips_noprev(r)
			# n <= 2:
			inline_strike(r)
			inline_vapor(r)
			inline_under(r)
		try:
			bot.answer_inline_query(update.inline_query.id, r, cache_time = 0)
		except BadRequest:
			clean_results(n = n+1)

	try:
		clean_results()
	except RecursionError as e:
		print('RecursionError: ' + e.__str__())

def add_handlers(dp, group):
	for i in [
		InlineQueryHandler(inlinequery),
	]: dp.add_handler(i, group)
