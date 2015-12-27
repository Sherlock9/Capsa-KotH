import itertools
import random
import re
import subprocess
import sys

### Next on the list
# 1. Who has 3 of Diamonds starts first #### DONE
# 2. Determining when a round is finished #### DONE
## (All PASS or no higher hands possible NONE_POSSIBLE)
# 3. Determining when a game is over #### DONE
## If games end when one Player has 0 cards,
## games usually end before rounds do (check for GAME_END before ROUND_END)
# 4. Write up a sample bot, maybe two: one Random, one Poker_Pair_Single
#### Random is DONE. Bot that can detect poker hands? Not so much
# 5. Write up communicating with bots #### DONE
### SUB-PROBLEMS OF COMM
## 1. Sending hand, last_played, round_num
## 2. Receiving now_playing (and adjusting hand to match) or "PASS"

players = []
discards = []

# fill with regexes for straight,flush,full house,straight flush,four of a kind
regexes = []

suits = ["S", "H", "C", "D"]
ranks = ["2", "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3"]
deck = []
card_values = [''.join(i) for i in itertools.product(ranks, suits)]

def make_deck():
    global deck
    deck = [''.join(i) for i in itertools.product(ranks, suits)]
    random.shuffle(deck)

def deal():
    global deck
    cut = random.randint(1, 51)
    cards = deck[:cut] + deck[cut:]
    for i in range(13):
        for j in range(4):
            players[j].hand.append(cards.pop(0))

def check_bad_hand(hand, l_played=[], r_num=0):
    global players
    bad_hand = False
    # check for correct number of cards
    if r_num:
        if len(hand) != r_num:
            bad_hand = True
            players = players[1:] + players[:1]
        if bad_hand:
            return bad_hand, False
    # check for all cards not already played before
    for card in hand:
        if card in discards:
            bad_hand = True
            players = players[1:] + players[:1]
    return value_check(hand, l_played, r_num, bad_hand)

def value_check(hand, l_played, r_num, bad_hand=False):
    wins_outright = False

    # if the hand is already bad, quit
    if bad_hand: return bad_hand, wins_outright

    # if r_num == 0
    r_num = r_num or len(hand)

    # if None played yet
    if l_played == []:
        if "2S" in hand and (r_num == 1 or r_num == 2):
            wins_outright = True
        return bad_hand, wins_outright

    # check for more value than last played
    if r_num == 1:
        # if the card isn't at a lower index (higher value), bad
        if card_values.index(hand[0]) >= card_values.index(l_played[0]):
            bad_hand = True
        if hand == ["2S"]:
            wins_outright = True

    elif r_num == 2:
        if hand[0][0] != hand[1][0]:
            return True, wins_outright
        # if the rank of both pairs is the same
        elif hand[0][0] == l_played[0][0]:
            # if the spade isn't with the hand, bad
            if hand[0][0]+"S" not in hand:
                bad_hand = True
        else:
            # if the pair is lower than previously played, bad
            if ranks.index(hand[0][0]) >= ranks.index(l_played[0][0]):
                bad_hand = True
        if "2S" in hand:
            wins_outright = True

    elif r_num == 5:
        # for four of a kind, straight flush, full house, flush, straight
        # in that order
        h_match = [0,0,0,0,0]
        p_match = [0,0,0,0,0]
        h = "".join(hand)
        p = "".join(l_played)
        h_ranks = set(h[::2])
        p_ranks = set(p[::2])
        fullhouse_h = ""
        fullhouse_p = ""
        four_h = ""
        four_p = ""

        # if straight
        a = sorted([ranks.index(i) for i in h_ranks])
        b = sorted([ranks.index(i) for i in p_ranks])
        c = [min(a)+i for i in range(5)]
        d = [min(b)+i for i in range(5)]
        if a == c:
            h_match[4] = 1
        if b == d:
            p_match[4] = 1

        # if flush
        for i in suits:
            if len(set(h[1::2])) == 1:
                h_match[3] = 1
            if len(set(p[1::2])) == 1:
                p_match[3] = 1

        # if full_house
        if len(h_ranks) == 2:
            for i in h_ranks:
                if h[::2].count(i) == 3:
                    h_match[2] = 1
                    fullhouse_h = i
        if len(p_ranks) == 2:
            for i in p_ranks:
                if p[::2].count(i) == 3:
                    p_match[2] = 1
                    fullhouse_h = i

        # if straight AND flush
        if h_match[4] and h_match[3]:
            h_match[1] = 1
        if p_match[4] and h_match[3]:
            p_match[1] = 1

        # if four-of-a-kind
        if len(h_ranks) == 2:
            for i in h_ranks:
                if h[::2].count(i) == 4:
                    h_match[0] = 1
                    four_h = i
        if len(p_ranks) == 2:
            for i in p_ranks:
                if p[::2].count(i) == 4:
                    p_match[0] = 1
                    four_p = i
        if four_h == "2":
            wins_outright = True

        # for debugging
        # print(h_match, p_match)

        # and now the actual comparison part

        if sum(h_match) == 0 or sum(p_match) == 0:
            return True, wins_outright

        if h_match.index(1) > p_match.index(1):
            bad_hand = True

        elif h_match.index(1) == p_match.index(1):
            val = h_match.index(1)

            # if two straights
            if val == 4:
                # if h < p (index of h > index of p)
                if min(a) > min(b):
                    bad_hand = True
                elif min(a) == min(b):
                    # if the suit of h_max < suit of p_max
                    e = h.index(ranks[min(a)])
                    f = p.index(ranks[min(b)])
                    if suits.index(h[e+1]) > suits.index(h[e+1]):
                        bad_hand = True

            # if two flushes
            elif val == 3:
                if suits.index(h[1]) > suits.index(p[1]):
                    bad_hand = True
                elif suits.index(h[1]) == suits.index(p[1]) and min(a) > min(b):
                    bad_hand = True

            # if two full houses
            elif val == 2:
                if ranks.index(fullhouse_h) > ranks.index(fullhouse_p):
                    bad_hand = True

            # if two straight flushes
            elif val == 1:
                # if h < p (index of h > index of p)
                if min(a) > min(b):
                    bad_hand = True
                elif min(a) == min(b):
                    # if the suit of h_max < suit of p_max
                    if suits.index(h[1]) > suits.index(p[1]):
                        bad_hand = True

            # if two four-of-a-kinds
            elif val == 0:
                if ranks.index(four_h) > ranks.index(four_p):
                    bad_hand = True
    else:
        # if it's any other size of hand, bad
        bad_hand = True
    return bad_hand, wins_outright

def play_game():
    global players, discards
    make_deck()
    deal()
    for i in range(4):
        if players[i].has_3D():
            players = players[i:] + players[:i]
    current = 0
    first_round = 1
    # if we've tried three times, and the bot fails, PASS
    tries = 0
    while True:
        # a new round
        print("ROUND_START")
        game_won = False
        last_played = []
        round_num = 0
        passed = []
        winning = False
        ### determine who last won

        first_hand = players[0].play(last_played, round_num, first_round)
        print(first_hand)

        # No passing for the first player in a round
        # unless they mess up three times
        if first_hand == "PASS":
            continue

        # check for bad
        bad_hand, winning = check_bad_hand(first_hand)
        # if bad, retry
        if bad_hand:
            if tries < 3:
                tries += 1
            else:
                tries = 0
                passed.append(players[0])
                players = players[1:] + players[:1]
            continue

        # set the round_num up
        round_num = len(first_hand)
        discards += first_hand
        last_played += [first_hand]
        players[0].remove(first_hand)
        first_round = 0
        tries = 0

        while True:
            # if game_end
            for i in players:
                if i.hand == []:
                    print(i.name, "is the winner!")
                    for i in players:
                        print(len(i.hand))
                    game_won = True
            if game_won:
                break

            # if round_end
            if len(passed) == 3 or winning:
                for i in range(4):
                    if players[i] not in passed:
                        players = players[i:] + players[:i]
                        break
                passed = []
                print("END_ROUND")
                break

            # on with the game
            current = (current + 1) % 4
            if players[current] in passed:
                continue
            hand = players[current].play(last_played, round_num, first_round)
            if hand[0] == "PASS":
                passed.append(players[current])
                print("PASS", current)
                continue
            bad_hand, winning = check_bad_hand(hand, last_played[-1], round_num)
            # if bad, retry
            if bad_hand:
                if tries <= 2:
                    tries += 1
                else:
                    tries = 0
                    passed.append(players[current])
                    print("PASS", current)
                current = (current - 1) % 4
                continue
            discards += hand
            last_played += [hand]
            players[current].remove(hand)
            tries = 0
            print(hand)
        if game_won:
            break

class Player:
    '''
    last_played is the list of hands that have been played (Knowing how fast
        the cards' values are rising may help the bots in their strategy)

    round_num is how many cards per hand in this round (singles, pairs or
        five-card poker hands) are being played.
    '''
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.last_played = []
        self.round_num = 0

    def has_3D(self):
        return "3D" in self.hand

    def remove(self, hand):
        for i in hand:
            self.hand.remove(i)

    def play(self, last_played, round_num, first_round=0):
        cards_played = self.communicate(last_played, round_num, first_round)        return cards_played

    def communicate(self, last_played, round_num, first_round=0):
        instr = "{}\n".format(','.join(self.hand))
        instr += "{}\n".format(round_num)
        instr += "{}\n".format(first_round)
        for i in range(len(last_played)):
            instr += "{}\n".format(','.join(last_played[i]))

        bot = subprocess.Popen(["python", "bots\\"+self.name],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               universal_newlines = True)
        cards_played = bot.communicate(input=instr)[0].strip().split(",")
        return cards_played

if __name__ == "__main__":
##    players = [Player("random_bot.py"), Player("random_bot.py"), Player("next_up.py"), Player("next_up.py")]
    for name in sys.argv[1:]:
        players.append(Player(name))
    if len(players) != 4:
        raise ValueError
    play_game()
