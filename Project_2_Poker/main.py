from deck import Card
from mcts import run_mcts
import sys

def parse_cards(card1, card2):
    """
    Parses two card strings and creates Card objects
    Args: card1_str (str), card2_str (str)
    Returns: list[Card] or a string with usage format
    """
    if len(card1) != 2 or len(card2) != 2:
        return "Cards must be in format like 'JD' or 'QS'"
    return [Card(card1[0].upper(), card1[1].upper()), Card(card2[0].upper(), card2[1].upper())]

def main():
    """Handles command-line arguments, runs the MCTS simulation, and prints the result"""
    if len(sys.argv) != 3:
        print("Usage: python main.py [card1] [card2]. Example: python main.py JD QC")
        return

    hand = parse_cards(sys.argv[1], sys.argv[2])
    print(f"Running MCTS for hand: {hand[0]} {hand[1]}")
    estimated_winrate = run_mcts(hand, iterations=1000)
    print(f"Estimated Win Rate: {estimated_winrate:.3f}")

if __name__ == "__main__":
    main()