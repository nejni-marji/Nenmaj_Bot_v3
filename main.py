#!/usr/bin/env python3
from os import execl
from datetime import datetime

from share.constants import root_dir

with open(root_dir + 'cache/start.txt', 'w') as f:
	f.write(datetime.now().strftime('%s.%f'))
	f.close()

print('[    0.000000] running')
execl(root_dir + 'bot.py', '--')
