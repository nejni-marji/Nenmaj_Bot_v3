#!/usr/bin/env python3
import re
from random import randint
from itertools import permutations

from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from share.data import owner
from bin.background import background

'''
This stuff is basically Nenmaj's soul. It's old and crappy, but such is the
life of Nenmaj. I can't bring myself to not include at least some of this in
Nenmaj 2.0, but I have to get rid of a lot of it. The plan is to eventually
rewrite this so that instead of calling bot_resp() a bunch of times, I'll
just have a database file somewhere that I load, and from that I'll read all
the responses I want to include.

For the time being, though, this code is gonna be garbage. Beautiful garbage.

Update (2018-10-14): This code is now being incorporated into Nenmaj 3.0, and
I actually do plan on refactoring it this time, but I'm not sure how I want to
do that.
'''

@background
def text_parse(bot, update):
	text = update.message.text
	user = update.message.from_user

	def check_at_bot():
		bot_named = re.search('(rel|nen)maj', text.lower())
		try:
			bot_replied = update.message.reply_to_message.from_user.id == bot.id
		except:
			bot_replied = False
		bot_pm = update.message.chat_id > 0
		at_bot = bot_named or bot_replied or bot_pm
		my_bot = re.search('\\b(m(y|ia) (ro)?boto?|(ro)?boto? mia)\\b', text.lower())
		master = (at_bot or my_bot) and user.id == owner
		return at_bot or master

	def bot_resp(
			pattern,
			response,
			chance = 5,
			words = True,
			markdown = False,
			call = 'text',
		):

		# if words, add word boundaries to the regex pattern
		if words: # kwarg: words
			pattern = '\\b(%s)\\b' % pattern # arg: pattern

		# match by pattern
		match = re.search(pattern, text, flags = re.I) # arg: pattern

		# declare this dict
		bot_kwargs = {}
		# we always want to do this
		bot_kwargs['reply_to_message_id'] = update.message.message_id
		# we might want to do this
		if markdown:
			bot_kwargs['parse_mode'] = ParseMode.MARKDOWN

		# Bob
		if update.message.from_user.id == owner:
			bob = update.message.from_user.first_name
		else:
			bob = 'Bob'

		is_pm = update.message.chat_id > 0
		if match and chance and (randint(1, chance) == 1 or is_pm or check_at_bot()): # kwarg: chance
			# these are the only variables that can be embedded into the bot's
			# response strings
			response = response.format( # arg: response
				text = update.message.text,
				match = match.group(),
				match_lower = match.group().lower(),
				match_upper = match.group().upper(),
				match_capitalize = match.group().capitalize(),
				username = update.message.from_user.username,
				first_name = update.message.from_user.first_name,
				last_name = update.message.from_user.last_name,
				bob = bob,
			)

			# be able to send different message types
			call_list = { # kwarg: call
				'text': bot.send_message,
				'photo': bot.send_photo,
			}

			# run the call function with the relevant args and kwargs
			return call_list[call]( # kwarg: call
				update.message.chat_id,
				response, # arg: response
				**bot_kwargs
			)

			return True

		else:
			return False

	def bot_responses():
		# Various simple responses to text stimulus.
		if True: # general responses
			bot_resp(
				"^same( \w+)?$",
				"same",
			)
			bot_resp(
				"aesthetic",
				"ａｅｓｔｈｅｔｉｃ",
			)
			bot_resp(
				"#poste",
				"mdr, ĉu vere?",
				words = False,
			)
			bot_resp(
				"Skype|Skajpo?n?",
				"http://stallman.org/skype.html",
				chance = 1
			)
			bot_resp(
				"fuck m(e|y life)",
				"_Later?_",
				chance = 1,
				markdown = True,
			)
			bot_resp(
				"Sponge ?Bob|Square ?Pants",
				"I think the funny part was\nWith SpongeBob was just sigen\nOUT of nowhere\nAnd squeaked word was like\ncan't BELIEVE IT",
			)
			bot_resp(
				"Pizza Hut|Taco Bell",
				"http://youtu.be/EQ8ViYIeH04",
				#markdown = True, # not required here
			)
			bot_resp(
				#"Jesus (fucking|effing) Christ",
				"Jesus (fuck|eff|frigg)ing? Christ",
				"Looks more like Jesus fucking Noah to me.",
				chance = 0,
			)
		if check_at_bot(): # respond to vocative
			bot_resp(
				'h(eyo?|ello|[ao]?i|owdy)|yo|oi|greetings|salutations|sup|'
				+ 'good ((eve|mor)ning|day|afternoon)',
				'{match_capitalize}, {first_name}!',
			)
			bot_resp(
				'thanks',
				'No prob, {bob}!',
			)
			bot_resp(
				#'i love (you|nenmaj)|ily|(you|nenmaj) is( the)? best (ro)?bot',
				'i love (you|nenmaj)|ily|(nenmaj is|you are)( the)? best (ro)?bot',
				'>///< senpai noticed me!',
			)
			bot_resp(
				'fuc?k (off|(yo)?u)|i hate (yo)?u|sod off|'
				+ 'you(\'?re? (dumb?|stupid)| suck)',
				'Please forgive me, I\'m only human!',
			)
			bot_resp(
				's+h+|be (quie|silen)t|shut up',
				'You can\'t tell me to be quiet!',
			)
			bot_resp(
				"(rel|nenmaj) irl|open[- ]source|source code|foss",
				#"AgADAwADrKcxGxf4GEwgaG2kIA2BeI30hjEABLCGgdjm9eXSgEYBAAEC",
				"AgADAwADs6cxG7F2IU5xnR7ZCnfs6VEHhzEABKIU0x2zu1zMa4oBAAEC",
				call = 'photo',
			)
		elif not check_at_bot(): # when someone greets a group
			hello_list = ['hi', 'hello', 'hey', 'heyo']
			hello = hello_list[randint(0, len(hello_list) - 1)].capitalize()
			# response for when someone greets a group
			bot_resp(
				'h(i|ello|eyo?),? ((y\'?)?all|everyone|people|ppl)',
				hello + ', {first_name}!',
			)
		if True and check_at_bot(): # respond to vocative (eo)
			for i in permutations(['mi', 'amas', 'vin']):
				bot_resp(
					' '.join(i),
					'Kaj ankaŭ {match_lower}, {first_name}!',
				)
			bot_resp(
				'saluton',
				'Resaluton, {first_name}!',
			)
			bot_resp(
				'sal',
				'Resal, {first_name}!',
			)
			# I'm sorry but this regex is just too powerful to use
			bot_resp(
				'bo(vin|n((eg)?an ?)?(m(aten|oment|am)|vesper|nokt(mez)?|'
				+ '(post(?=...mez))?t(emp|ag(er|mez)?)))(eg)?on',
				'Kaj {match_lower} al vi, {first_name}!',
			)
			bot_resp(
				'dank(eg)?on',
				'Nedankinde, {first_name}!',
			)
			bot_resp(
				'hej',
				'Kion vi volas, {first_name}?',
			)
			bot_resp(
				'fek al (vi|nenmaj)|(vi|nenmaj) (estas stulta|stultas)',
				'Bonvole pardonu min, mi estas nur homo!',
			)
			bot_resp(
				'ŝ+|(kviet|silent|ferm)iĝu',
				'Vi ne povas kvietigi min!',
			)
		elif False and not check_at_bot(): # when someone greets a group (eo)
			sal_list = ['sal', 'saluton', 'resal']
			sal = sal_list[randint(0, len(sal_list) - 1)].capitalize()
			# response for when someone greets a group
			bot_resp(
				'sal(uton)?( al|,?) (vi )?(c[hx]|ĉ)iuj?( vi)?',
				sal + ', {first_name}!',
			)

	def bot_ayylmao():
		# Don't do anything if @theayybot is present.
		try:
			theayybot = bot.get_chat_member(update.message.chat_id,
				139464619
			)
			if theayybot.status == 'member':
				return None
		except:
			pass

		if randint(0,5) == 0:
			rip = "in pepperoni"
		else:
			rip = "in pieces"
		if bot_resp(
			"rip|^rip\\w+",
			rip,
			#["in pieces", "in pepperoni"]
			chance = 1,
		):
			return None

		res_ayy = re.search('\\b(ayy+)\\b', text.lower())
		res_lmao = re.search('\\b(lmao+)\\b', text.lower())

		if res_ayy and res_lmao:
			resp = 'ayy lmao'
		elif res_ayy:
			resp = 'lmao' + 'o' * len(res_ayy.group()[3:])
		elif res_lmao:
			resp = 'ayy' + 'y' * len(res_lmao.group()[4:])
		if res_ayy or res_lmao:
			bot.send_message(update.message.chat_id,
				resp,
			)

	if True:
		bot_responses()
		bot_ayylmao()

def add_handlers(dp, group):
	for i in [
		MessageHandler(Filters.text, text_parse),
	]: dp.add_handler(i, group)
