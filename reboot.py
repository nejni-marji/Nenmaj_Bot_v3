#!/usr/bin/env python3
from os import execl
#from os.path import dirname
from sys import argv

from share.constants import root_dir

text = 'rebooting'
num = len(text)

resp = []
resp.append('*' * (num + 6))
resp.append('== %s ==' % text.upper())
resp.append('*' * (num + 6))

print('\n'.join(resp))

#with open(dirname(__file__) + '/../cache/reboot.txt', 'w') as f:
with open(root_dir + 'cache/reboot.txt', 'w') as f:
	f.write(argv[1])
	f.close()

#execl(dirname(__file__) + '/../main.py', '--')
execl(root_dir + 'main.py', '--')
