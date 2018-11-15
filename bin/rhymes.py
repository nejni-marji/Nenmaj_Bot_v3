#!/usr/bin/env python3
from sys import argv
from urllib.request import urlopen
from re import findall
from html import unescape

def get_www_rhymes(query):
	url = 'https://www.rhymezone.com/r/rhyme.cgi?Word=%s&typeofrhyme=perfect&org1=syl&org2=l&org3=y'
	try:
		text = urlopen(url % query).read().decode('utf-8')
	except UnicodeEncodeError:
		print('UnicodeEncodeError: returning []')
		return []
	pattern = '<a class=(?:"d r"|r) href="d=[^-].*?">(.*?)</a>'

	matches = findall(pattern, text)

	rhymes = [
		unescape(i).replace('\xa0', ' ')
		for i
		in matches
	]
	return rhymes
