import pandas as pd
from simulation import play_hand, create_deck

# runs n simulations of blackjack and tracks wins, losses, and ties
def simulate(n):
    # counters to track outcomes
    wins = 0
    losses = 0
    ties = 0
    # run n hands, each with a fresh deck
    for i in range(n):
        deck = create_deck()
        result = play_hand(deck)
        # increment the appropriate counter based on result
        if result == "win":
            wins += 1
        elif result == "loss":
            losses += 1
        else:
            ties += 1
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Ties: {ties}")
    print(f"Win rate: {wins / n * 100:.2f}%")

simulate(10000)