#!/usr/bin/env python3
import re
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import ParseMode
from telegram.ext import InlineQueryHandler

from bin.background import background
from share.constants import fullwidth

strike = re.compile('<s>(.(?!</s>))+.</s>')
def strike_text(text):
	pretext = text
	match = strike.search(text)
	while match:
		text = text.replace(
			match.group(),
			'\u0336'.join(list(match.group()[3:-4])) + '\u0336',
			1
		)
		match = strike.search(text)
	if pretext == text:
		text = '\u0336'.join(list(text)) + '\u0336'
	return text

@background
def inlinequery(bot, update):
	inline_query = update.inline_query
	query = update.inline_query.query
	results = []

	def inline_help():
		help_text = [
			'If you\'ve never used an inline bot before, <a href="https://telegram.org/blog/inline-bots">click here!</a>',
			'Otherwise, read on.',
			'',
			'Strikethrough:',
			'foo →  f̶o̶o̶',
			'&lt;s&gt;foo&lt;/s&gt; bar →  f̶o̶o̶ bar',
			'',
			'Vaporwave:',
			'foo → ｆｏｏ',
			'',
			'Markdown:',
			'_italics_, *bold*, `code` → <i>italics</i>, <b>bold</b>, <code>code</code>',
			'You can also embed URLs:',
			'[example](https://example.org) → <a href="https://example.org">example</a>',
			'',
			'If you want to display an image preview of the URL, select "Markdown (Preview)". If not, select "Markdown (No Preview)".',
		]

		text = '\n'.join(help_text)
		desc = 'Don\'t know how this works? Click here!'
		results.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Help and Usage',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.HTML,
				disable_web_page_preview = True
			)
		))

	def strikethrough():
		text = strike_text(query)
		desc = text
		results.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Strikethrough',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.MARKDOWN
			)
		))

	def vaporwave():
		text = ''
		for i in list(query):
			if i == ' ':
				text += '    '
			elif i not in fullwidth:
				text += i
			else:
				text += chr(0xFEE0 + ord(i))
		desc = text
		results.append(InlineQueryResultArticle(id = uuid4(),
			title = 'Vaporwave',
			description = desc,
			input_message_content = InputTextMessageContent(
				text
			)
		))

	def markdown_noprev():
		text = query
		desc = text
		results.append(InlineQueryResultArticle(id=uuid4(),
			title = 'Markdown (No Preview)',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.MARKDOWN,
				disable_web_page_preview = True
			)
		))

	def markdown_prev():
		text = query
		desc = text
		results.append(InlineQueryResultArticle(id=uuid4(),
			title = 'Markdown (Preview)',
			description = desc,
			input_message_content = InputTextMessageContent(
				text,
				parse_mode = ParseMode.MARKDOWN,
				disable_web_page_preview = False
			)
		))

	inline_help()
	if query:
		strikethrough()
		vaporwave()
		markdown_noprev()
		markdown_prev()

	# send inline query results
	bot.answer_inline_query(update.inline_query.id, results, cache_time = 0)

def add_handlers(dp, group):
	for i in [
		InlineQueryHandler(inlinequery),
	]: dp.add_handler(i, group)
