import random

class Card:
    def __init__(self, card_num, suit):
        """Initializes a Card with a number and a suit"""
        self.card_num = card_num
        self.suit = suit

    def __repr__(self):
        return f"{self.card_num}{self.suit}"

    def __eq__(self, other):
        """Checks equality of card objects"""
        return isinstance(other, Card) and self.card_num == other.card_num and self.suit == other.suit

    def __hash__(self):
        """Allows card objects to be stored in sets and dictionary keys"""
        return hash((self.card_num, self.suit))

class Deck:
    def __init__(self):
        self.reset()

    def reset(self):
        """Creates a full deck and shuffles it"""
        card_nums = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['C', 'D', 'H', 'S']
        self.cards = [Card(card_num, suit) for card_num in card_nums for suit in suits]
        random.shuffle(self.cards)

    def deal_card(self):
        """
        Deals one card from the top of the deck
        Args: N/A
        Returns: Card or None 
        """
        if not self.cards:
            return None
        return self.cards.pop()
    
    def deal_hand(self, num_cards):
        """
        Deals a specified number of cards as a list
        Args: num_cards (int)
        Returns: list[Card]
        """
        return [self.deal_card() for _ in range(num_cards)]
    
    def remove_card(self, card):
        """
        Removes a specific card from the deck
        Args: card (Card)
        Returns: N/A
        """
        self.cards = [c for c in self.cards if c != card]

    def remaining_cards(self):
        """
        Returns a copy of the list of cards still in the deck
        Args: N/A
        Returns: list[Card]
        """
        return self.cards[:]