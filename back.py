from collections import Counter
import math
import itertools
import time
import re
import json
import textwrap
import os
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, jsonify, render_template, request, url_for

# configure application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Eh2tsCh3HkAOh96f@localhost/master?unix_socket=/cloudsql/poker-pro:us-central1:poker-pro"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

sql_app = SQLAlchemy(app)
sql_app.init_app(app)

db = sql_app.session()


"""
Cards are defined by integers from 1 to 52
"""

# defines the card ranks
# ((card_num - 1) % 13) + 1 = index of rank
card_ranks = {
	1: "ace",
	2: "2",
	3: "3",
	4: "4",
	5: "5",
	6: "6",
	7: "7",
	8: "8",
	9: "9",
	10: "10",
	11: "jack",
	12: "queen",
	13: "king"
}

# defines the card suits
# (card_num - 1) // 13 = index of suit
card_suits = {
	0: "hearts",
	1: "spades",
	2: "diamonds",
	3: "clubs"
}

# delineates the various hand types
hand_types = [
	"royal_flush",
	"straight_flush",
	"four_of_a_kind",
	"full_house",
	"flush",
	"straight",
	"three_of_a_kind",
	"two_pair",
	"one_pair"
]


# function that gets the identity of a hand of cards
# input should be list of integer representations of cards
def identity(cards):
	# setup hand dict
	hand = {
		"royal_flush": False,
		"straight_flush": False,
		"four_of_a_kind": False,
		"full_house": False,
		"flush": False,
		"straight": False,
		"three_of_a_kind": False,
		"two_pair": False,
		"one_pair": False
	}

	# unofficial royal straight variable
	royal_straight = False

	# generate lists of ranks and suits
	ranks = []
	suits = []
	for card in cards:
		rank = ((card - 1) % 13) + 1
		suit = (card - 1) // 13
		ranks.append(rank)
		suits.append(suit)

	# create Counter objects
	counter_suits = Counter(suits)
	counter_ranks = Counter(ranks)

	# check if there is a straight
	# first remove duplicates from rank list and sort
	unique_elements = list(counter_ranks)
	unique_elements.sort()
	# check if there are even five unique elements to test
	if len(unique_elements) >= 5:
		# check if the straight is royal
		if set(unique_elements).issubset([10, 11, 12, 13, 1]):
			royal_straight = True
			hand["straight"] = True
		else:
			# check if there exists a straight
			tick = -1
			in_a_row = 1
			# loop through every element
			for elem in unique_elements:
				# if element is one more than prior tick
				if elem == tick + 1:
					# add one to in_a_row
					in_a_row += 1
					# check if we have reached a straight
					if in_a_row == 5:
						hand["straight"] = True
						break
				else:
					# reset in_a_row
					in_a_row = 1
				# adjust tick
				tick = elem

	# check if there is a flush
	# get the frequency of the most common suit
	suit_frequency = counter_suits.most_common(1)[0][1]

	# if this frequency is greater than or equal to five
	# flush territory
	if suit_frequency >= 5:
		hand["flush"] = True
		# check for royal flush
		if royal_straight is True:
			hand["royal_flush"] = True

		# check for straight flush
		if hand["straight"] is True:
			hand["straight_flush"] = True

	# check two most frequent ranks
	rank_frequency = counter_ranks.most_common(2)
	# check if most frequent rank occurs 4 times
	if rank_frequency[0][1] == 4:
		# four of a kind
		hand["four_of_a_kind"] = True
		hand["three_of_a_kind"] = True
		hand["one_pair"] = True
	# check if most frequent rank occurs 3 times
	elif rank_frequency[0][1] == 3:
		# three of a kind
		hand["three_of_a_kind"] = True
		hand["one_pair"] = True
		# check if the second most frequent occurs twice
		if rank_frequency[1][1] == 2:
			# full house!
			hand["full_house"] = True
			hand["two_pair"] = True
	# check if the most frequent occurs twice
	elif rank_frequency[0][1] == 2:
		hand["one_pair"] = True
		# check if second most frequent occurs twice
		if rank_frequency[1][1] == 2:
			hand["two_pair"] = True

	# return the hand dictionary
	return hand


# function that checks a hand and returns the outcomes that remain possible
# intended to expedite the analysis of a hand by limiting unnecessary
# usage of the database
# important to note: this only applies to five card combinations
def possible_identity(cards):
	# setup hand dict
	# all are initially set to true
	possible = {
		"royal_flush": True,
		"straight_flush": True,
		"four_of_a_kind": True,
		"full_house": True,
		"flush": True,
		"straight": True,
		"three_of_a_kind": True,
		"two_pair": True,
		"one_pair": True
	}

	# generate lists of ranks and suits
	ranks = []
	suits = []
	for card in cards:
		rank = ((card - 1) % 13) + 1
		suit = (card - 1) // 13
		ranks.append(rank)
		suits.append(suit)

	# create Counter objects
	counter_suits = Counter(suits)
	counter_ranks = Counter(ranks)

	# get number of cards
	num_of_cards = len(cards)

	# get the frequency of the most common suit
	suit_frequency = counter_suits.most_common(1)[0][1]

	# check if flush possibility exists
	if suit_frequency < num_of_cards:
		# impossible to get a flush
		possible["royal_flush"] = False
		possible["straight_flush"] = False
		possible["flush"] = False

	# check if straight possibility exists
	# first remove duplicates from rank list and sort
	unique_elements = list(counter_ranks)
	unique_elements.sort()
	# get number of unique elements
	num_unique = len(unique_elements)
	# if there are any duplicates
	if num_unique != num_of_cards:
		# five card straight is impossible
		possible["straight"] = False
		possible["straight_flush"] = False
		possible["royal_flush"] = False

	# if straight is not looking royal
	if not all(card in [1, 10, 11, 12, 13] for card in ranks):
		possible["royal_flush"] = False

	# if the difference between the elements is >= 5
	if unique_elements[-1] - unique_elements[0] >= 5:
		# five card straight is impossible
		possible["straight"] = False
		possible["straight_flush"] = False
		possible["royal_flush"] = False

	# check two most frequent ranks
	rank_frequency = counter_ranks.most_common(2)

	# check if most frequent rank occurs less than num_of_cards - 1
	if rank_frequency[0][1] < num_of_cards - 1:
		# impossible to get a four of a kind
		possible["four_of_a_kind"] = False

	# check if most frequent rank occurs less than num_of_cards - 2
	if rank_frequency[0][1] < num_of_cards - 2:
		# impossible to get three of a kind or full house
		possible["three_of_a_kind"] = False
		possible["full_house"] = False

	# check if there are two possible frequencies
	if num_unique >= 2:
		# check if top two frequencies add up to less than num_of_cards - 1
		if rank_frequency[0][1] + rank_frequency[1][1] < num_of_cards - 1:
			# impossible to get two pair
			possible["two_pair"] = False

	return possible


# function that analyzes a hand
def analyze(hand, hand_type="all"):
	# hand must be list of integers
	if type(hand) is not list:
		raise ValueError("Invalid hand", hand)

	# hand type must be "all" or a specified hand type
	if hand_type != "all" and hand_type not in hand_types:
		raise ValueError("Invalid hand_type", hand_type)

	# create returnable dictionary
	odds = {}

	# get number of cards in hand
	num_of_cards = len(hand)

	# calculate total hands possible with given cards
	total_hands = nCr(52 - num_of_cards, 5 - num_of_cards)

	# check if hand is empty
	if not hand:
		# if it is, return the normal probabilities of hands
		# https://en.wikipedia.org/wiki/Poker_probability
		odds["royal_flush"] = nCr(4, 1) / total_hands
		odds["straight_flush"] = nCr(10, 1) * nCr(4, 1) / total_hands
		odds["four_of_a_kind"] = nCr(13, 1) * nCr(12, 1) * nCr(4, 1) / total_hands
		odds["full_house"] = nCr(13, 1) * nCr(4, 3) * nCr(12, 1) * nCr(4, 2) / total_hands
		odds["flush"] = nCr(13, 5) * nCr(4, 1) / total_hands
		odds["straight"] = nCr(10, 1) * nCr(4, 1) ** 5 / total_hands
		odds["three_of_a_kind"] = nCr(13, 1) * nCr(4, 3) * nCr(12, 2) * nCr(4, 1) ** 2 / total_hands
		odds["two_pair"] = nCr(13, 2) * nCr(4, 2) ** 2 * nCr(11, 1) * nCr(4, 1) / total_hands
		odds["one_pair"] = nCr(13, 1) * nCr(4, 2) * nCr(12, 3) * nCr(4, 1) ** 3 / total_hands + odds["two_pair"] + \
		                   odds["three_of_a_kind"] + odds["four_of_a_kind"] + odds["full_house"]
		return odds

	# sort hand
	hand.sort()

	# hand must not have more than 5 cards
	if num_of_cards > 5:
		raise ValueError("Invalid hand length")

	# if hand is five cards, just run it through the identity function
	if num_of_cards == 5:
		hid = identity(hand)
		odds = {}
		for h_type, bool in hid.items():
			if bool is True:
				odds[h_type] = 1
			else:
				odds[h_type] = 0
		return odds

	# get hand id in string form
	str_id = ''.join([str(num).zfill(2) for num in hand])

	# first check the possible identity of the given hand
	sql = "SELECT * FROM master.possible WHERE id = :id;"
	possible = db.execute(sql, {"id": str_id}).fetchone()

	# build regex statements that find cards in id strings from db
	regex = ""
	for card in hand:
		# cards must be padded with 0 if single digit
		card_str = str(card).zfill(2)

		# (?=regex1)(?=regex2) means match both regex 1 and 2
		# ^ is start of string
		# (\d{2})?{0,4} is zero to four optional two digit numbers
		# $ is end of string
		regex += "(?=^((\d{2})?){0,4}" + card_str + "((\d{2})?){0,4}$)"

	# get list of card ranks
	ranks = [(card - 1) % 13 + 1 for card in hand]
	num_unique = len(list(Counter(ranks)))
	# if request is for all types of odds
	if hand_type == "all":
		# query database for all types of hand
		for i in hand_types:
			# check if it is even possible to get hand with given cards
			if possible[i] is False:
				odds[i] = 0
			elif i == "one_pair":
				# see if there are less unique card ranks than cards
				if not num_unique < len(hand):
					# then we don't already have a pair
					# pair probability can be easily calculated with unique cards
					# this is important because calculating one-pair takes a long time to calculate
					if len(hand) == 4:
						odds[i] = .25
					if len(hand) == 3:
						odds[i] = .387755
					if len(hand) == 2:
						odds[i] = .461224
					if len(hand) == 1:
						odds[i] = .492917
				else:
					# we already have a pair
					odds[i] = 1
			else:
				matches = hand_matches(db, i, regex, str_id)
				# calculate odds of receiving appropriate hand
				odds[i] = matches / total_hands
	else:
		# check if it is even possible to get hand with given cards
		if possible[hand_type] is False:
			odds[hand_type] = 0
		elif hand_type == "one_pair":
			# see if there are less unique card ranks than cards
			if not num_unique < len(hand):
				# then we don't already have a pair
				# pair probability can be easily calculated with unique cards
				if len(hand) == 4:
					odds[hand_type] = .25
				if len(hand) == 3:
					odds[hand_type] = .387755
				if len(hand) == 2:
					odds[hand_type] = .461224
				if len(hand) == 1:
					odds[hand_type] = .492917
			else:
				# we already have a pair
				odds[hand_type] = 1
		else:
			matches = hand_matches(db, hand_type, regex, str_id)
			# calculate odds of receiving appropriate hand
			odds[hand_type] = matches / total_hands

	return odds


# queries database for certain type of hand and returns count of matched hand
def hand_matches(db, hand_type, regex, str_id):

	# check if we already have matches information
	matches_sql_check = "SELECT * FROM master.matches WHERE id = :id;"
	check = db.execute(matches_sql_check, {"id": str_id}).fetchone()
	# check if row exists
	if check is None:
		# if row doesnt exist, create it
		matches_sql_insert = "INSERT INTO master.matches (id) VALUES(:id);"
		db.execute(matches_sql_insert, {"id": str_id})
		db.commit()
	elif check[hand_type] is not None:
		# if we already have the right information, return that
		return check[hand_type]

	# otherwise lets get that information
	# initialize counting variable
	count = 0
	# create sql string
	sql = "SELECT id FROM master.hands WHERE " + hand_type + " = 1;"
	# execute string
	returned = db.execute(sql)
	# count up hands that are matches
	for line in returned:
		id = line[0]
		match = re.match(regex, id)
		if match is not None:
			count += 1
	# put answer in db
	matches_sql_update = "UPDATE master.matches SET " + hand_type + "=:count WHERE id=:id;"
	db.execute(matches_sql_update, {"count": count, "id": str_id})
	db.commit()
	return count


# function that builds out the database holding
# all possible poker hands and their rank
def build_hands_db():
	# start timer
	start = time.process_time()

	# create all possible five card combinations
	combos = itertools.combinations(list(range(1, 53)), 5)

	# get length of combos
	total_combos = nCr(52, 5)

	# try to create table in db
	# already created table
	# sql = "CREATE TABLE 'hands' ('id' TEXT PRIMARY KEY NOT NULL, " \
	#       "'royal_flush' BOOLEAN, 'straight_flush' BOOLEAN, 'four_of_a_kind' " \
	#       "BOOLEAN, 'full_house' BOOLEAN, 'flush' BOOLEAN, 'straight' BOOLEAN, " \
	#       "'three_of_a_kind' BOOLEAN, 'two_pair' BOOLEAN, 'one_pair' BOOLEAN);"
	# db.execute(sql)

	# initialize counter
	counter = 0

	# loop through combinations
	for combo in combos:

		# turn tuple combo into list
		list(combo)

		# get hand identity of combo
		hid = identity(combo)

		# get hand id in string form
		str_id = ''.join([str(num).zfill(2) for num in combo])

		# create values for safe sql entry
		values = {
			"id": str_id,
			"royal_flush": hid["royal_flush"],
			"straight_flush": hid["straight_flush"],
			"four_of_a_kind": hid["four_of_a_kind"],
			"full_house": hid["full_house"],
			"flush": hid["flush"],
			"straight": hid["straight"],
			"three_of_a_kind": hid["three_of_a_kind"],
			"two_pair": hid["two_pair"],
			"one_pair": hid["one_pair"]
		}

		sql = "INSERT INTO master.hands (id, royal_flush, straight_flush, four_of_a_kind, full_house, flush, " \
	           "straight, three_of_a_kind, two_pair, one_pair) VALUES(:id, :royal_flush, :straight_flush, " \
	           ":four_of_a_kind, :full_house, :flush, " \
	           ":straight, :three_of_a_kind, :two_pair, :one_pair);"


		# try to execute sql
		try:
			db.execute(sql, values)
			db.commit()
		except:
			print("error: "+str_id)

		# update output window
		print("{:4f}".format(counter / total_combos))
		counter += 1

	# close connection with database
	db.close()

	# end timer
	end = time.process_time()
	# print total time it took to create db
	print(end - start)


# function that builds out the database holding
# all possibilities of a poker hand given 4, 3, 2, of 1 cards
def build_possible_db():
	# start timer
	start = time.process_time()

	# create all possible four, three, two, and one card combinations
	combos4 = itertools.combinations(list(range(1, 53)), 4)
	combos3 = itertools.combinations(list(range(1, 53)), 3)
	combos2 = itertools.combinations(list(range(1, 53)), 2)
	combos1 = itertools.combinations(list(range(1, 53)), 1)


	# get length of combos
	total_combos = nCr(52, 4) + nCr(52, 3) + nCr(52, 2) + nCr(52, 1)

	# open connection to db
	db = sqlite3.connect("poker.db")

	# try to create table in db
	sql = "CREATE TABLE 'possible' ('id' TEXT PRIMARY KEY NOT NULL, " \
	      "'royal_flush' BOOLEAN, 'straight_flush' BOOLEAN, 'four_of_a_kind' " \
	      "BOOLEAN, 'full_house' BOOLEAN, 'flush' BOOLEAN, 'straight' BOOLEAN, " \
	      "'three_of_a_kind' BOOLEAN, 'two_pair' BOOLEAN, 'one_pair' BOOLEAN);"
	try: db.execute(sql)
	except: pass

	# initialize counter
	counter = 0

	# loop through combinations
	for combo in itertools.chain(combos4, combos3, combos2, combos1):

		# turn tuple combo into list
		list(combo)

		# get possible identity of combo
		hid = possible_identity(combo)

		# get hand id in string form
		str_id = ''.join([str(num).zfill(2) for num in combo])

		# create values for safe sql entry
		values = {
			"id": str_id,
			"royal_flush": hid["royal_flush"],
			"straight_flush": hid["straight_flush"],
			"four_of_a_kind": hid["four_of_a_kind"],
			"full_house": hid["full_house"],
			"flush": hid["flush"],
			"straight": hid["straight"],
			"three_of_a_kind": hid["three_of_a_kind"],
			"two_pair": hid["two_pair"],
			"one_pair": hid["one_pair"]
		}

		# try to execute sql
		try:
			db.execute("INSERT INTO possible (id, royal_flush, straight_flush, four_of_a_kind, full_house, flush, " \
			           "straight, three_of_a_kind, two_pair, one_pair) VALUES(:id, :royal_flush, :straight_flush, "
			           ":four_of_a_kind, :full_house, :flush, " \
			           ":straight, :three_of_a_kind, :two_pair, :one_pair);", values)
			db.commit()
		except:
			pass

		# update output window
		print("{:4f}".format(counter / total_combos))
		counter += 1

	# close connection with database
	db.close()

	# end timer
	end = time.process_time()
	# print total time it took to create db
	print(end - start)


# function that describes cards
def describe(cards):
	# for each card in input, print name and suit
	for card in cards:
		suit = card_suits[(card - 1) // 13]
		rank = card_ranks[((card - 1) % 13) + 1]
		print("{} of {}".format(rank, suit))
	print("------")


# choose math function
def nCr(n, r):
	return math.factorial(n) / math.factorial(r) / math.factorial(n - r)


if __name__ == "__main__":

	build_hands_db()

	pass
