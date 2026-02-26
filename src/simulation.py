import numpy as np

suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']


# creates a standard 52 card deck as a list of strings
def create_deck():
    deck = [f"{rank} of {suit}" for rank in ranks for suit in suits]
    return deck

# takes a card string and returns its numerical blackjack value
# face cards = 10, Ace = 11, number cards = face value
def card_value(card):
    rank = card.split(' of ')[0]
    if rank == 'J' or rank == 'Q' or rank == 'K':
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

# deals 2 random cards from the deck and removes them so they cant be dealt again
def deal_hand(deck):
    hand = []
    for i in range(2):
        card = str(np.random.choice(deck))
        hand.append(card)
        deck.remove(card)
    return hand

# calculates the total value of a hand, handles Ace as 1 or 11 to avoid busting
def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        value = card_value(card)
        if 'A' in card:
            aces += 1
        total += value
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

# deals hands to player and dealer, runs both turns, and determines the winner
def play_hand(deck):
    player_hand = deal_hand(deck)
    dealer_hand = deal_hand(deck)

    if hand_value(player_hand) == 21:
        print("Blackjack! You win!")
        return

    player_hand = player_turn(player_hand, deck)
    dealer_hand = dealer_turn(dealer_hand, deck)

    player_total = hand_value(player_hand)
    dealer_total = hand_value(dealer_hand)

    print(f"Player hand: {player_hand}, total: {player_total}")
    print(f"Dealer hand: {dealer_hand}, total: {dealer_total}")

    if player_total > 21:
        print("Bust! You lose!")
    elif dealer_total > 21:
        print("Dealer busts! You win!")
    elif player_total > dealer_total:
        print("You win!")
    elif player_total < dealer_total:
        print("Dealer wins!")
    else:
        print("Push! It's a tie!")

# function to hit if card deck is less then 17 (required for sim)
def player_turn(hand, deck):
    while hand_value(hand) < 17:
        card = str(np.random.choice(deck))
        hand.append(card)
        deck.remove(card)
    return hand

# automatically plays the dealer's turn, hits until total is 17 or above
def dealer_turn(hand, deck):
    while hand_value(hand) < 17:
        card = str(np.random.choice(deck))
        hand.append(card)
        deck.remove(card)
    return hand
        
deck = create_deck()
print(len(deck))
play_hand(deck)
print(len(deck))