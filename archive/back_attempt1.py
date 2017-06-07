import math
import random

from archive.definitions import *


# choose math function
def nCr(n, r):
    return math.factorial(n) / math.factorial(r) / math.factorial(n-r)

# add Card function
# return all possible hands given input hands + 1 card
def addCard(hands):
    # initialize returnable hands
    returnable_hands = []
    # loop through every hand
    for hand in hands:
        for i in range(1, 52):
            # check if card already exists in hand
            if i not in hand:
                # create copy of the passed hand
                temp_hand = list(hand)
                # add new card to temp_hand
                temp_hand.append(i)
                # sort temp_hand
                temp_hand.sort
                # add temp_hand to returnable
                returnable_hands.append(temp_hand)
    return returnable_hands


# build Hands function
def buildHands(hand):
    # calculate necessary cards to add
    needed_cards = 6 - len(hand)
    # initialize returnable hands variable to inputted hand
    hands = [hand]
    for i in range(needed_cards):
        hands = addCard(hands)
    return hands


# function that describes cards
def describe(cards):
    # for each card in input, print name and suit
    for card in cards:
        suit = card_suits[card // 13]
        rank = card_ranks[((card - 1) % 13) + 1]
        print("{} of {}".format(rank, suit))
    print("------")


# analyze hand
def analyze(hand):
    # sort hand
    hand.sort()
    # get all possible poker hands given hand
    created_hands = buildHands(hand)
    print(len(created_hands))
    # for hand in created_hands:
    #     print(hand)



# hand class
class Hand:
    
    # initialize
    def __init__(self, cards):
        # all cards should be of type int
        if all(type(card) is not int for card in cards):
            raise TypeError("int types required to init Hand")
        self.cards = cards

    # allow for length calculations
    def __len__(self):
        return len(self.cards)

    # add card to hand
    def __add__(self, new_card):
        # other should be of type int
        if type(new_card) is not int:
            raise TypeError("not int type added to Hand")
        # other cannot be a duplicate of an already existing card
        if new_card in self.cards:
            return None
        # add card_int to cards list
        self.cards.append(new_card)
        return self

    # make hand iterable over cards
    def __getitem__(self, index):
        return self.cards[index]


# deck class
class Deck:
    
    # initialize
    def __init__(self):

        # add all playing cards (52) to deck.cardsin
        self.cardsin = list(range(1, 52))

        # shuffle the deck
        random.shuffle(self.cardsin)

    # make deck iterable over cardsin
    def __getitem__(self, index):
        return self.cardsin[index]

    # deal card(s) off top of deck
    def deal(self, n = 1):
        
        # initialize list of returned cards
        dealt = []
        
        # remove appropriate number of cards from deck and add to returned list
        for i in range(n):
            dealt.append(self.cardsin.pop())
            
        return dealt