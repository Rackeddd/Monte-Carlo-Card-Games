import numpy as np
from collections import Counter
from itertools import combinations

# ---------------------------------------------------------------------------
# Shared deck utilities
# ---------------------------------------------------------------------------

suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']


def create_deck():
    """Creates a standard 52-card deck as a list of strings."""
    return [f"{rank} of {suit}" for rank in ranks for suit in suits]


def create_shoe(num_decks=8):
    """Creates a shoe of multiple decks (standard for baccarat)."""
    return create_deck() * num_decks


def _draw(deck):
    """Draws a uniformly random card from deck in-place and returns it."""
    idx = np.random.randint(0, len(deck))
    card = deck[idx]
    deck[idx] = deck[-1]  # swap with last for O(1) removal
    deck.pop()
    return card


# ---------------------------------------------------------------------------
# Blackjack
# ---------------------------------------------------------------------------

def bj_card_value(card):
    """Returns blackjack point value: face cards=10, Ace=11, numbers=face."""
    rank = card.split(' of ')[0]
    if rank in ('J', 'Q', 'K'):
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)


def bj_hand_value(hand):
    """Calculates blackjack hand total; treats Aces as 1 when needed to avoid bust."""
    total = 0
    aces = 0
    for card in hand:
        total += bj_card_value(card)
        if card.split(' of ')[0] == 'A':
            aces += 1
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def _bj_deal(deck):
    return [_draw(deck), _draw(deck)]


def _bj_player_turn(hand, deck):
    """Basic strategy: hit until hard 17+."""
    while bj_hand_value(hand) < 17:
        hand.append(_draw(deck))
    return hand


def _bj_dealer_turn(hand, deck):
    """Dealer hits on soft 16 or less, stands on 17+."""
    while bj_hand_value(hand) < 17:
        hand.append(_draw(deck))
    return hand


def play_blackjack_hand(deck):
    """
    Plays one hand of blackjack against the dealer.

    Returns
    -------
    outcome : str  — 'win', 'loss', or 'tie'
    payout  : float — net multiplier on the wager
                      (1.5 for natural blackjack, 1.0 normal win,
                       0.0 tie/push, -1.0 loss)
    """
    player = _bj_deal(deck)
    dealer = _bj_deal(deck)

    player_bj = bj_hand_value(player) == 21 and len(player) == 2
    dealer_bj = bj_hand_value(dealer) == 21 and len(dealer) == 2

    if player_bj and dealer_bj:
        return 'tie', 0.0
    if player_bj:
        return 'win', 1.5
    if dealer_bj:
        return 'loss', -1.0

    player = _bj_player_turn(player, deck)
    dealer = _bj_dealer_turn(dealer, deck)

    p_total = bj_hand_value(player)
    d_total = bj_hand_value(dealer)

    if p_total > 21:
        return 'loss', -1.0
    if d_total > 21:
        return 'win', 1.0
    if p_total > d_total:
        return 'win', 1.0
    if p_total < d_total:
        return 'loss', -1.0
    return 'tie', 0.0


# ---------------------------------------------------------------------------
# Baccarat
# ---------------------------------------------------------------------------

def bac_card_value(card):
    """Baccarat values: 10/J/Q/K = 0, Ace = 1, 2-9 = face value."""
    rank = card.split(' of ')[0]
    if rank in ('10', 'J', 'Q', 'K'):
        return 0
    elif rank == 'A':
        return 1
    else:
        return int(rank)


def bac_hand_value(hand):
    """Baccarat hand value: sum of card values mod 10."""
    return sum(bac_card_value(c) for c in hand) % 10


def play_baccarat_hand(deck, bet='player'):
    """
    Plays one hand of baccarat using official Punto Banco drawing rules.

    Parameters
    ----------
    deck : list  — mutable card list (use create_shoe for realistic play)
    bet  : str   — 'player', 'banker', or 'tie'

    Returns
    -------
    outcome : str   — 'win', 'loss', or 'tie' (from bettor's perspective)
    payout  : float — net multiplier on the wager
                      player win = 1.0, banker win = 0.95 (5% commission),
                      tie win = 8.0, push = 0.0, loss = -1.0
    """
    player_hand = [_draw(deck), _draw(deck)]
    banker_hand = [_draw(deck), _draw(deck)]

    p = bac_hand_value(player_hand)
    b = bac_hand_value(banker_hand)

    # Natural 8 or 9 → no additional cards
    if p < 8 and b < 8:
        # Player drawing rule: draw on 0-5, stand on 6-7
        player_third_val = None
        if p <= 5:
            third = _draw(deck)
            player_hand.append(third)
            player_third_val = bac_card_value(third)
            p = bac_hand_value(player_hand)

        # Banker drawing rule
        b = bac_hand_value(banker_hand)
        if player_third_val is None:
            # Player stood — banker draws on 0-5
            if b <= 5:
                banker_hand.append(_draw(deck))
        else:
            ptv = player_third_val
            if b <= 2:
                banker_hand.append(_draw(deck))
            elif b == 3 and ptv != 8:
                banker_hand.append(_draw(deck))
            elif b == 4 and 2 <= ptv <= 7:
                banker_hand.append(_draw(deck))
            elif b == 5 and 4 <= ptv <= 7:
                banker_hand.append(_draw(deck))
            elif b == 6 and ptv in (6, 7):
                banker_hand.append(_draw(deck))
            # b == 7: banker always stands

    p = bac_hand_value(player_hand)
    b = bac_hand_value(banker_hand)

    if p > b:
        winner = 'player'
    elif b > p:
        winner = 'banker'
    else:
        winner = 'tie'

    # Map winner + bet type → outcome and payout
    if bet == 'player':
        if winner == 'player':
            return 'win', 1.0
        if winner == 'banker':
            return 'loss', -1.0
        return 'tie', 0.0   # tie is a push on player bet

    if bet == 'banker':
        if winner == 'banker':
            return 'win', 0.95  # 5% vigorish
        if winner == 'player':
            return 'loss', -1.0
        return 'tie', 0.0       # tie is a push on banker bet

    # 'tie' bet
    if winner == 'tie':
        return 'win', 8.0
    return 'loss', -1.0


# ---------------------------------------------------------------------------
# Poker — Texas Hold'em
# ---------------------------------------------------------------------------

_RANK_ORDER = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
}

_HAND_RANK = {
    'High Card': 0, 'One Pair': 1, 'Two Pair': 2, 'Three of a Kind': 3,
    'Straight': 4, 'Flush': 5, 'Full House': 6,
    'Four of a Kind': 7, 'Straight Flush': 8, 'Royal Flush': 9,
}


def _rank_val(card):
    return _RANK_ORDER[card.split(' of ')[0]]


def _suit(card):
    return card.split(' of ')[1]


def evaluate_5card_hand(hand):
    """
    Evaluates a 5-card poker hand.

    Returns a comparable tuple (hand_rank_int, tiebreaker_tuple) where a
    higher tuple beats a lower one.  Suitable for max() comparisons.
    """
    vals = sorted([_rank_val(c) for c in hand], reverse=True)
    suits_seen = [_suit(c) for c in hand]
    counts = Counter(vals)
    freq = sorted(counts.values(), reverse=True)

    is_flush = len(set(suits_seen)) == 1
    unique_vals = sorted(counts.keys())
    is_straight = len(counts) == 5 and (unique_vals[-1] - unique_vals[0] == 4)
    # Wheel: A-2-3-4-5
    is_wheel = unique_vals == [2, 3, 4, 5, 14]
    if is_wheel:
        is_straight = True
        vals = [5, 4, 3, 2, 1]

    if is_straight and is_flush:
        label = 'Royal Flush' if vals[0] == 14 else 'Straight Flush'
        return (_HAND_RANK[label], tuple(vals))

    if freq[0] == 4:
        quad = max(r for r, c in counts.items() if c == 4)
        kick = max(r for r, c in counts.items() if c == 1)
        return (_HAND_RANK['Four of a Kind'], (quad, kick))

    if freq == [3, 2]:
        trip = max(r for r, c in counts.items() if c == 3)
        pair = max(r for r, c in counts.items() if c == 2)
        return (_HAND_RANK['Full House'], (trip, pair))

    if is_flush:
        return (_HAND_RANK['Flush'], tuple(vals))

    if is_straight:
        return (_HAND_RANK['Straight'], tuple(vals))

    if freq[0] == 3:
        trip = max(r for r, c in counts.items() if c == 3)
        kickers = tuple(sorted((r for r, c in counts.items() if c == 1), reverse=True))
        return (_HAND_RANK['Three of a Kind'], (trip,) + kickers)

    if freq[:2] == [2, 2]:
        pairs = tuple(sorted((r for r, c in counts.items() if c == 2), reverse=True))
        kick = max(r for r, c in counts.items() if c == 1)
        return (_HAND_RANK['Two Pair'], pairs + (kick,))

    if freq[0] == 2:
        pair = max(r for r, c in counts.items() if c == 2)
        kickers = tuple(sorted((r for r, c in counts.items() if c == 1), reverse=True))
        return (_HAND_RANK['One Pair'], (pair,) + kickers)

    return (_HAND_RANK['High Card'], tuple(vals))


def best_hand_from_7(cards):
    """Returns the best 5-card hand score from 7 cards (Texas Hold'em)."""
    return max(evaluate_5card_hand(list(combo)) for combo in combinations(cards, 5))


def hand_name_from_score(score_tuple):
    """Returns the hand name string from a score tuple."""
    rank_int = score_tuple[0]
    for name, val in _HAND_RANK.items():
        if val == rank_int:
            return name
    return 'Unknown'


def play_poker_hand(num_players=6):
    """
    Simulates one hand of Texas Hold'em.

    Player index 0 is the hero (our tracked player).
    Returns 'win', 'loss', or 'tie'.
    """
    deck = create_deck()
    # In-place Fisher-Yates shuffle via numpy for speed
    np.random.shuffle(deck)

    # Deal hole cards (2 per player)
    hole_cards = [[deck.pop(), deck.pop()] for _ in range(num_players)]

    # Burn + flop
    deck.pop()
    community = [deck.pop(), deck.pop(), deck.pop()]
    # Burn + turn
    deck.pop()
    community.append(deck.pop())
    # Burn + river
    deck.pop()
    community.append(deck.pop())

    scores = [best_hand_from_7(hole_cards[i] + community) for i in range(num_players)]
    best = max(scores)
    winners = [i for i, s in enumerate(scores) if s == best]

    if 0 not in winners:
        return 'loss'
    return 'win' if len(winners) == 1 else 'tie'
