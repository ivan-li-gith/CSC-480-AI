import math
from itertools import combinations
from evaluator import evaluate_hand
from deck import Deck
from random import sample

class MCTSNode:
    def __init__(self, state, parent=None, stage='root', player_hand=None):
        self.state = state              
        self.parent = parent
        self.children = {}              
        self.wins = 0
        self.visits = 0
        self.stage = stage
        self.player_hand = player_hand
        self.untried_actions = []

    def ucb1(self, n, c=math.sqrt(2)):
        """
        Calculates the UCB1 score
        Args: n (int), c (math.sqrt(2))
        Returns: float
        """
        return (self.wins / self.visits) + c * math.sqrt(math.log(n) / self.visits)

    def is_fully_expanded(self):
        """Checks if all possible actions from this node have been tried"""
        return len(self.untried_actions) == 0

    def best_child(self, c=math.sqrt(2)):
        """
        Selects the child with the highest UCB1 score
        Args: c (math.sqrt(2))
        Returns: MCTSNode
        """
        n = sum(child.visits for child in self.children.values())   # total number of simulations
        best_score = -1
        best_node = None

        # finds child with highest ucb1 score
        for child in self.children.values():
            ucb_score = child.ucb1(n, c)
            if ucb_score > best_score:
                best_score = ucb_score
                best_node = child

        return best_node
    
    def expand(self):
        """
        Expands the tree by creating one new child node from an untried action
        Args: N/A
        Returns: MCTSNode
        """
        if not self.untried_actions:
            return None
        action = self.untried_actions.pop()
        new_state = self.state + list(action)   # new game state after action so what the new hand is after each stage 
        next_stage = self.get_next_stage()
        child = MCTSNode(new_state, parent=self, stage=next_stage, player_hand=self.player_hand)    # new leaf
        self.children[action] = child   # adds child to parent tree
        return child

    def get_next_stage(self):
        """
        Gets the next stage of the game
        Args: N/A
        Returns: stage (string)
        """
        stages = ['root', 'opponent', 'flop', 'turn', 'river']
        next_stage_idx = stages.index(self.stage) + 1

        if next_stage_idx < len(stages):
            return stages[next_stage_idx]
        else:
            return 'done'

    def backpropagate(self, result):
        """
        Updates the tree after the simulations
        Args: result (float)
        Returns: N/A
        """
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)


def sample_opponent_hands(player_hand):
    """
    Samples opponents possible hand from the remaining 50 cards
    Args: player_hand (list[Card])
    Returns: list[tuple[Card]]
    """
    deck = Deck()
    deck.remove_card(player_hand[0])
    deck.remove_card(player_hand[1])
    combos = list(combinations(deck.remaining_cards(), 2))
    k = min(1000, len(combos))
    return sample(combos, k)


def sample_flops(used_cards):
    """
    Samples possible flops from the remaining cards
    Args: used_cards (list[Card])
    Returns: list[tuple[Card]]
    """
    deck = Deck()
    remaining = [card for card in deck.cards if card not in used_cards]
    combos = list(combinations(remaining, 3))
    k = min(1000, len(combos))
    return sample(combos, k)

def sample_turns(used_cards):
    """
    Samples possible turns from the remaining cards
    Args: used_cards (list[Card])
    Returns: list[tuple[Card]] 
    """
    deck = Deck()
    remaining = [card for card in deck.cards if card not in used_cards]
    k = min(1000, len(remaining))
    return sample([(card,) for card in remaining], k)   # needs to be in card, for formatting in tuples (caused errors earlier)

def sample_rivers(used_cards):
    """
    Samples possible rivers from the remaining cards
    Args: used_cards (list[Card])
    Returns: list[tuple[Card]]
    """
    deck = Deck()
    remaining = [card for card in deck.cards if card not in used_cards]
    k = min(1000, len(remaining))
    return sample([(card,) for card in remaining], k) 

def rollout_simulation(player_hand, opponent_hand, board):
    """
    Compares player and opponent hands with the board to the winner
    Args: player_hand (list[Card]), opponent_hand (list[Card]), board (list[Card])
    Returns: 1, 0, or 0.5 depending on who wins
    """
    full_player_hand = player_hand + board
    full_opponent_hand = opponent_hand + board

    player_rank = evaluate_hand(full_player_hand)
    opponent_rank = evaluate_hand(full_opponent_hand)

    if player_rank > opponent_rank:
        return 1
    elif player_rank < opponent_rank:
        return 0
    else:
        return 0.5  # tie

def simulate_to_end(node):
    """
    Performs the MCTS simulation
    Args: node (MCTSNode)
    Returns: 1, 0, or 0.5 depending on who wins
    """
    # remove all used cards from the deck
    deck = Deck()
    used = node.player_hand + node.state
    for card in used:
        deck.remove_card(card)

    # assigns cards based on the stage of the game
    opponent_hand = []
    community_cards = []
    if node.stage == 'opponent':
        opponent_hand = node.state
    elif node.stage == 'flop':
        opponent_hand = node.state[:2]
        community_cards = node.state[2:]
    elif node.stage == 'turn':
        opponent_hand = node.state[:2]
        community_cards = node.state[2:]
    elif node.stage == 'river':
        opponent_hand = node.state[:2]
        community_cards = node.state[2:]
    
    # ensures that the opponent has a hand 
    if not opponent_hand:
        opponent_hand = deck.deal_hand(2)
    
    # ensures that the board has cards 
    cards_needed = 5 - len(community_cards)
    if cards_needed > 0:
        community_cards.extend(deck.deal_hand(cards_needed))

    return rollout_simulation(node.player_hand, opponent_hand, community_cards)

def run_mcts(player_hand, iterations=1000):
    """
    Runs the MCTS algorithm for a given hand
    Args: player_hand (list[Card]), iterations (int, 1000)
    Returns: float
    """
    root = MCTSNode(state=[], stage='root', player_hand=player_hand)
    root.untried_actions = sample_opponent_hands(player_hand)

    for i in range(iterations):
        node = root

        # selection
        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        # expansion
        if not node.is_fully_expanded():
            child_node = node.expand()
            if child_node:
                used_cards = child_node.player_hand + child_node.state

                # depending on the stage is what will be sampled
                if child_node.stage == 'opponent':
                    child_node.untried_actions = sample_flops(used_cards)
                elif child_node.stage == 'flop':
                    child_node.untried_actions = sample_turns(used_cards)
                elif child_node.stage == 'turn':
                    child_node.untried_actions = sample_rivers(used_cards)
                node = child_node 

        # simulation/ backpropagation
        result = simulate_to_end(node)
        node.backpropagate(result)

    if root.visits == 0:
        return 0.0
    
    return root.wins / root.visits