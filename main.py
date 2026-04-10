"""
main.py — Monte Carlo Card Game Simulator
==========================================
Runs full Monte Carlo simulations for Blackjack, Baccarat, and Poker,
then prints aggregate statistics and saves visualisation plots.

Usage (from the project root):
    python main.py
"""

from src.analysis import (
    simulate_blackjack,
    simulate_baccarat,
    simulate_poker,
    simulate_poker_hand_distribution,
    streak_analysis,
    print_stats,
    print_streak_stats,
    plot_bankroll_curves,
    plot_win_loss_rates,
    plot_outcome_pie,
    plot_poker_hand_frequencies,
    plot_streak_distribution,
)

# ---------------------------------------------------------------------------
# Simulation parameters — adjust as desired
# ---------------------------------------------------------------------------
N_HANDS   = 10_000   # hands per simulation
BET_SIZE  = 10.0     # dollar wager per hand
N_PLAYERS = 6        # total players at poker table (including hero)
N_DECKS   = 8        # baccarat shoe size
BIG_BLIND = 2.0      # poker blind size (drives payout scaling)

# ---------------------------------------------------------------------------
# Run simulations
# ---------------------------------------------------------------------------
print("=" * 60)
print("  Monte Carlo Card Game Simulator")
print(f"  {N_HANDS:,} hands per game — bet size ${BET_SIZE:.0f}")
print("=" * 60)

print("\n[1/4]  Simulating Blackjack …")
bj_stats, bj_df = simulate_blackjack(n_hands=N_HANDS, bet_size=BET_SIZE)

print("[2/4]  Simulating Baccarat (player, banker, tie bets) …")
bac_p_stats, bac_p_df = simulate_baccarat(N_HANDS, bet='player', bet_size=BET_SIZE, num_decks=N_DECKS)
bac_b_stats, bac_b_df = simulate_baccarat(N_HANDS, bet='banker', bet_size=BET_SIZE, num_decks=N_DECKS)
bac_t_stats, bac_t_df = simulate_baccarat(N_HANDS, bet='tie',    bet_size=BET_SIZE, num_decks=N_DECKS)

print("[3/4]  Simulating Poker (Texas Hold'em) …")
poker_stats, poker_df = simulate_poker(n_hands=N_HANDS, num_players=N_PLAYERS, big_blind=BIG_BLIND)

print("[4/4]  Sampling poker hand frequencies (50,000 hands) …")
hand_freq = simulate_poker_hand_distribution(n_hands=50_000)

# ---------------------------------------------------------------------------
# Print statistics
# ---------------------------------------------------------------------------
print("\n\n── Aggregate Statistics ─────────────────────────────────────")
for stats in (bj_stats, bac_p_stats, bac_b_stats, bac_t_stats, poker_stats):
    print_stats(stats)

# ---------------------------------------------------------------------------
# Streak analysis
# ---------------------------------------------------------------------------
print("\n\n── Win Streak Analysis ──────────────────────────────────────")
streak_pairs = [
    (bj_df,    'Blackjack'),
    (bac_p_df, 'Baccarat (player)'),
    (bac_b_df, 'Baccarat (banker)'),
    (poker_df, "Poker (Texas Hold'em)"),
]
for df, name in streak_pairs:
    streak = streak_analysis(df, min_streak=3)
    print_streak_stats(streak, name)

# ---------------------------------------------------------------------------
# Poker hand frequency table
# ---------------------------------------------------------------------------
print("\n\n── Poker Hand Frequency Distribution (50,000 sampled hands) ─")
print(hand_freq.to_string())

# ---------------------------------------------------------------------------
# Visualisations
# ---------------------------------------------------------------------------
print("\n\n── Generating plots … ───────────────────────────────────────")

plot_win_loss_rates(
    [bj_stats, bac_p_stats, bac_b_stats, poker_stats],
    save_path='win_loss_rates.png',
)

plot_bankroll_curves(
    [bj_df, bac_p_df, bac_b_df, poker_df],
    labels=[
        'Blackjack',
        'Baccarat — player',
        'Baccarat — banker',
        f"Poker ({N_PLAYERS}P Hold'em)",
    ],
    save_path='bankroll_curves.png',
)

plot_outcome_pie(bj_df,    'Blackjack',         save_path='outcomes_blackjack.png')
plot_outcome_pie(bac_p_df, 'Baccarat (Player)', save_path='outcomes_baccarat_player.png')
plot_outcome_pie(bac_b_df, 'Baccarat (Banker)', save_path='outcomes_baccarat_banker.png')
plot_outcome_pie(poker_df, "Poker (Hold'em)",   save_path='outcomes_poker.png')

plot_poker_hand_frequencies(hand_freq, save_path='poker_hand_frequencies.png')

# streak distribution for blackjack as a representative example
bj_streak = streak_analysis(bj_df, min_streak=3)
plot_streak_distribution(bj_streak, 'Blackjack', save_path='streaks_blackjack.png')

print("\nDone. All plots saved to the project root.")
