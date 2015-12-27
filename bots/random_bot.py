# random_bot.py

import random
import re
import sys

the_input = re.split('\n', re.sub(r'[^A-Z0-9,[]\n]+', '', sys.stdin.read()))

#print(the_input)

len_0 = len((the_input)[0])
hand = the_input[0].split(',')

round_num = int(the_input[1])

first_round = int(the_input[2])

len_1 = len((the_input)[-1])
last_played = the_input[-1].split(',')

#print(hand, round_num, last_played)
if round_num != 0 and round_num != 1:
    output = "PASS"
else:
    output = hand[random.randint(0,len(hand)-1)]
if first_round:
    output = "3D"
print(output)
