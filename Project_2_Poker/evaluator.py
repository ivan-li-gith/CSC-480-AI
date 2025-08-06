from itertools import combinations
from collections import Counter

COMBO_VALUE_MAP = {"high_card": 0, "one_pair": 1, "two_pair": 2,
                    "three_of_a_kind": 3, "straight": 4, "flush": 5,
                    "full_house": 6, "four_of_a_kind": 7, "straight_flush": 8, "royal_flush": 9}

CARD_VALUE_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                  '7': 7, '8': 8, '9': 9, 'T': 10,
                  'J': 11, 'Q': 12, 'K': 13, 'A': 14}

def check_straight(values):
    """
    Checks if a given list of card values contains a straight or a wheel
    Args: values (list[int])
    Returns: bool: True or False
    """
    # turn to set to remove duplicate and turn back to list so sort from high to low 
    values = list(set(values))
    values.sort(reverse=True)

    # if it is a straight the difference between the high card and low card will be 4
    for i in range(len(values) - 4):
        if values[i] - values[i + 4] == 4:
            return True

    # checking wheel (ace low straight)
    ace_low_straight = set([14, 2, 3, 4, 5])
    if ace_low_straight.issubset(values):
        return True

    return False

def rank_five_card_hand(hand):
    """
    Evaluates a 5 card hand and determines its rank and tie-breaking values
    Args: hand (list[Card])
    Returns: tuple[int, list[int]] where it is (rank, list of cards)
    """
    values = sorted([CARD_VALUE_MAP[c.card_num] for c in hand], reverse=True)   # convert hand to its card value and sort it from high to low
    suits = [c.suit for c in hand]  # get all the suits from the hand to check if it is a flush
    value_counts = Counter(values)  # counts the how many of each card there is for 2/3/4 pairs and full house
    is_flush = len(set(suits)) == 1
    is_straight = check_straight(values)


    # royal and straight flushes
    if is_flush and is_straight:
        if max(values) == 14:
            return (9, values)  # royal 
        return (8, values)  # straight

    # four of a kind
    if 4 in value_counts.values():
        four_of_a_kind = next(value for value, count in value_counts.items() if count == 4) # gets the card that has a count of 4
        high_card = max([value for value in values if value != four_of_a_kind])
        return (7, [four_of_a_kind, high_card]) 

    # full house
    if 3 in value_counts.values() and 2 in value_counts.values():
        three_of_a_kind = next(value for value, count in value_counts.items() if count == 3) 
        pair = next(value for value, count in value_counts.items() if count == 2) 
        return (6, [three_of_a_kind, pair])  

    # flush
    if is_flush:
        return (5, values)

    # straight
    if is_straight:
        return (4, values)

    # three of a kind
    if 3 in value_counts.values():
        three_of_a_kind = next(value for value, count in value_counts.items() if count == 3) 
        high_cards = sorted([value for value in values if value != three_of_a_kind], reverse=True)[:2]
        return (3, [three_of_a_kind] + high_cards)

    # two pair
    if list(value_counts.values()).count(2) == 2:   # turn to list and check if there are 2 pairs 
        pairs = sorted([value for value, count in value_counts.items() if count == 2], reverse=True)
        kicker = max([value for value in values if value not in pairs])
        return (2, pairs + [kicker])

    # one pair
    if 2 in value_counts.values():
        pair = next(value for value, count in value_counts.items() if count == 2) 
        high_cards = sorted([value for value in values if value != pair], reverse=True)[:3]
        return (1, [pair] + high_cards)

    # high card
    return (0, values)

def evaluate_hand(cards):
    """
    Finds the best possible 5 card hand
    Args: cards (list[Card])
    Returns: tuple[int, list[int]]
    """
    best_rank = (-1, [])

    # combinations loops through all possible hands and ranks the hand 
    for combo in combinations(cards, 5):
        rank = rank_five_card_hand(combo)
        best_rank = max(best_rank, rank)
    return best_rank