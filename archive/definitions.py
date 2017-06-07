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
# card_num // 13 = index of suit
card_suits = {
    0: "hearts",
    1: "spades",
    2: "clubs",
    3: "diamonds"
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