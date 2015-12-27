# next_up.py

import itertools
import re
import sys

suits = ["S", "H", "C", "D"]
ranks = ["2", "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3"]
card_values = [''.join(i) for i in itertools.product(ranks, suits)]

the_input = re.split('\n', re.sub(r'[^A-Z0-9,[]\n]+', '', sys.stdin.read()))

hand = the_input[0].split(',')

round_num = int(the_input[1])

first_round = int(the_input[2])

last_played = the_input[-2].split(',')

if round_num != 0 and round_num != 1:
    output = "PASS"
else:
    output = 0
    try:
        index = card_values.index(last_played[0])
        for i in hand:
            if card_values.index(i) < index:
                output = i
        if not output:
            output = "PASS"
    except:
        output = hand[0]
if first_round:
    output = "3D"
print(output)
