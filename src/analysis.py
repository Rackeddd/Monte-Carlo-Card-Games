"""
analysis.py — Monte Carlo simulation engine and visualisation for:
  • Blackjack
  • Baccarat  (player bet, banker bet, tie bet)
  • Poker     (Texas Hold'em, configurable number of opponents)

Run via main.py from the project root:
    python main.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.simulation import (
    create_deck, create_shoe,
    play_blackjack_hand,
    play_baccarat_hand,
    play_poker_hand,
    hand_name_from_score,
    best_hand_from_7,
    _HAND_RANK,
)


# ---------------------------------------------------------------------------
# Monte Carlo — Blackjack
# ---------------------------------------------------------------------------

def simulate_blackjack(n_hands: int = 10_000, bet_size: float = 10.0) -> tuple:
    """
    Monte Carlo simulation of n_hands of blackjack.

    Each hand is dealt from a fresh 52-card deck (standard casino practice
    with continuous shuffle machines).

    Returns
    -------
    stats : dict   — aggregate statistics
    df    : DataFrame — per-hand results with running bankroll
    """
    records = []
    bankroll = 0.0

    for _ in range(n_hands):
        deck = create_deck()
        outcome, payout = play_blackjack_hand(deck)
        net = payout * bet_size
        bankroll += net
        records.append({'outcome': outcome, 'payout': payout,
                        'net': net, 'bankroll': bankroll})

    df = pd.DataFrame(records)
    wins   = int((df['outcome'] == 'win').sum())
    losses = int((df['outcome'] == 'loss').sum())
    ties   = int((df['outcome'] == 'tie').sum())

    stats = {
        'game':           'Blackjack',
        'n_hands':        n_hands,
        'wins':           wins,
        'losses':         losses,
        'ties':           ties,
        'win_rate':       wins   / n_hands,
        'loss_rate':      losses / n_hands,
        'tie_rate':       ties   / n_hands,
        'house_edge':     -df['payout'].mean(),   # positive → house advantage
        'final_bankroll': bankroll,
        'max_bankroll':   df['bankroll'].max(),
        'min_bankroll':   df['bankroll'].min(),
        'avg_net_per_hand': df['net'].mean(),
    }
    return stats, df


# ---------------------------------------------------------------------------
# Monte Carlo — Baccarat
# ---------------------------------------------------------------------------

def simulate_baccarat(
    n_hands: int = 10_000,
    bet: str = 'player',
    bet_size: float = 10.0,
    num_decks: int = 8,
) -> tuple:
    """
    Monte Carlo simulation of n_hands of Baccarat.

    Parameters
    ----------
    bet : 'player' | 'banker' | 'tie'
        Ties are a push (0.0) on player/banker bets; an 8:1 payout on tie bet.
    num_decks : int
        Shoe size.  Standard casino baccarat uses 6 or 8 decks.

    Returns
    -------
    stats : dict
    df    : DataFrame
    """
    records = []
    bankroll = 0.0
    deck = create_shoe(num_decks)   # share a shoe across hands like a real casino

    for _ in range(n_hands):
        # Reshuffle when fewer than ~15 cards remain (cut-card rule approximation)
        if len(deck) < 15:
            deck = create_shoe(num_decks)
        outcome, payout = play_baccarat_hand(deck, bet=bet)
        net = payout * bet_size
        bankroll += net
        records.append({'outcome': outcome, 'payout': payout,
                        'net': net, 'bankroll': bankroll})

    df = pd.DataFrame(records)
    wins   = int((df['outcome'] == 'win').sum())
    losses = int((df['outcome'] == 'loss').sum())
    ties   = int((df['outcome'] == 'tie').sum())

    stats = {
        'game':           f'Baccarat ({bet} bet)',
        'n_hands':        n_hands,
        'wins':           wins,
        'losses':         losses,
        'ties':           ties,
        'win_rate':       wins   / n_hands,
        'loss_rate':      losses / n_hands,
        'tie_rate':       ties   / n_hands,
        'house_edge':     -df['payout'].mean(),
        'final_bankroll': bankroll,
        'max_bankroll':   df['bankroll'].max(),
        'min_bankroll':   df['bankroll'].min(),
        'avg_net_per_hand': df['net'].mean(),
    }
    return stats, df


def simulate_baccarat_all_bets(
    n_hands: int = 10_000,
    bet_size: float = 10.0,
    num_decks: int = 8,
) -> dict:
    """
    Convenience wrapper — simulates all three bet types in one call.

    Returns a dict with keys 'player', 'banker', 'tie', each containing
    (stats, df) tuples.
    """
    return {
        bet_type: simulate_baccarat(n_hands, bet=bet_type,
                                    bet_size=bet_size, num_decks=num_decks)
        for bet_type in ('player', 'banker', 'tie')
    }


# ---------------------------------------------------------------------------
# Monte Carlo — Poker (Texas Hold'em)
# ---------------------------------------------------------------------------

def simulate_poker(
    n_hands: int = 10_000,
    num_players: int = 6,
    big_blind: float = 2.0,
) -> tuple:
    """
    Monte Carlo simulation of n_hands of Texas Hold'em.

    Payout model (simplified pot odds):
      Win  → collect (num_players - 1) × big_blind  (net after posting blind)
      Loss → lose big_blind
      Tie  → push (0.0)

    Returns
    -------
    stats : dict
    df    : DataFrame with per-hand results and running bankroll
    """
    records = []
    bankroll = 0.0

    for _ in range(n_hands):
        outcome = play_poker_hand(num_players=num_players)
        if outcome == 'win':
            net = big_blind * (num_players - 1)
        elif outcome == 'loss':
            net = -big_blind
        else:
            net = 0.0
        bankroll += net
        records.append({'outcome': outcome, 'net': net, 'bankroll': bankroll})

    df = pd.DataFrame(records)
    wins   = int((df['outcome'] == 'win').sum())
    losses = int((df['outcome'] == 'loss').sum())
    ties   = int((df['outcome'] == 'tie').sum())

    stats = {
        'game':              f"Poker — Texas Hold'em ({num_players} players)",
        'n_hands':           n_hands,
        'wins':              wins,
        'losses':            losses,
        'ties':              ties,
        'win_rate':          wins   / n_hands,
        'loss_rate':         losses / n_hands,
        'tie_rate':          ties   / n_hands,
        'expected_win_rate': 1.0 / num_players,   # random-baseline
        'final_bankroll':    bankroll,
        'max_bankroll':      df['bankroll'].max(),
        'min_bankroll':      df['bankroll'].min(),
        'avg_net_per_hand':  df['net'].mean(),
    }
    return stats, df


def simulate_poker_hand_distribution(n_hands: int = 50_000) -> pd.Series:
    """
    Samples n_hands of 7-card Texas Hold'em to estimate the frequency of
    each hand category (High Card, One Pair, …, Royal Flush).

    Returns a Series indexed by hand name, values as percentages.
    """
    from src.simulation import create_deck, _draw, _HAND_RANK, best_hand_from_7

    hand_counts = Counter({name: 0 for name in _HAND_RANK})

    for _ in range(n_hands):
        deck = create_deck()
        np.random.shuffle(deck)
        # 2 hole cards + 5 community cards = 7 cards for the hero
        seven = [deck.pop() for _ in range(7)]
        score = best_hand_from_7(seven)
        name = hand_name_from_score(score)
        hand_counts[name] += 1

    ordered = [
        'High Card', 'One Pair', 'Two Pair', 'Three of a Kind',
        'Straight', 'Flush', 'Full House', 'Four of a Kind',
        'Straight Flush', 'Royal Flush',
    ]
    series = pd.Series(
        {name: hand_counts[name] / n_hands * 100 for name in ordered},
        name='frequency_%'
    )
    return series


# ---------------------------------------------------------------------------
# Streak analysis
# ---------------------------------------------------------------------------

def streak_analysis(df: pd.DataFrame, min_streak: int = 3) -> dict:
    """
    Analyses consecutive win streaks in a simulation result DataFrame.

    Returns
    -------
    dict with:
      streak_lengths   — list of all streak lengths observed
      max_streak       — longest winning streak
      prob_at_least_N  — dict mapping streak_len → P(occurring at least once)
      pct_in_streak    — % of hands that are part of any win streak ≥ min_streak
    """
    outcomes = df['outcome'].tolist()
    streak_lengths = []
    current = 0
    for o in outcomes:
        if o == 'win':
            current += 1
        else:
            if current > 0:
                streak_lengths.append(current)
            current = 0
    if current > 0:
        streak_lengths.append(current)

    max_streak = max(streak_lengths) if streak_lengths else 0
    n = len(outcomes)

    prob_at_least_N = {}
    for k in range(1, min(max_streak + 1, 11)):
        prob_at_least_N[k] = sum(1 for s in streak_lengths if s >= k) / n

    in_streak = sum(s for s in streak_lengths if s >= min_streak)
    pct_in_streak = in_streak / n * 100

    return {
        'streak_lengths':  streak_lengths,
        'max_streak':      max_streak,
        'prob_at_least_N': prob_at_least_N,
        'pct_in_streak':   pct_in_streak,
        'min_streak':      min_streak,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_stats(stats: dict) -> None:
    """Pretty-prints a stats dict returned by any simulate_* function."""
    print(f"\n{'=' * 56}")
    print(f"  {stats['game']}")
    print(f"{'=' * 56}")
    print(f"  Hands simulated   : {stats['n_hands']:>10,}")
    print(f"  Wins              : {stats['wins']:>10,}  ({stats['win_rate']*100:6.2f}%)")
    print(f"  Losses            : {stats['losses']:>10,}  ({stats['loss_rate']*100:6.2f}%)")
    print(f"  Ties / Pushes     : {stats['ties']:>10,}  ({stats['tie_rate']*100:6.2f}%)")
    if 'house_edge' in stats:
        sign = '+' if stats['house_edge'] >= 0 else ''
        print(f"  House edge        : {sign}{stats['house_edge']*100:>9.3f}%")
    if 'expected_win_rate' in stats:
        print(f"  Expected win rate : {stats['expected_win_rate']*100:>9.2f}%  (random baseline)")
    print(f"  Avg net / hand    : ${stats['avg_net_per_hand']:>+9.4f}")
    print(f"  Final bankroll    : ${stats['final_bankroll']:>+10,.2f}")
    print(f"  Peak bankroll     : ${stats['max_bankroll']:>+10,.2f}")
    print(f"  Lowest bankroll   : ${stats['min_bankroll']:>+10,.2f}")


def print_streak_stats(streak: dict, game_name: str) -> None:
    print(f"\n  [{game_name}] Streak analysis (min streak = {streak['min_streak']})")
    print(f"    Max consecutive wins : {streak['max_streak']}")
    print(f"    % hands in a streak  : {streak['pct_in_streak']:.2f}%")
    print("    P(streak ≥ N hands)  :")
    for k, p in streak['prob_at_least_N'].items():
        bar = '█' * int(p * 40)
        print(f"      N={k:>2}  {p*100:6.3f}%  {bar}")


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

def plot_bankroll_curves(
    dfs: list,
    labels: list,
    title: str = 'Bankroll Over Time — Monte Carlo Simulation',
    save_path: str = 'bankroll_curves.png',
) -> None:
    """Plots running bankroll for each game on a shared axis."""
    fig, ax = plt.subplots(figsize=(13, 6))
    colors = ['#2196F3', '#4CAF50', '#FF5722', '#9C27B0', '#FF9800']

    for df, label, color in zip(dfs, labels, colors):
        ax.plot(df.index, df['bankroll'], label=label, alpha=0.85,
                linewidth=1.0, color=color)

    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.4)
    ax.set_xlabel('Hand Number', fontsize=11)
    ax.set_ylabel('Net Bankroll ($)', fontsize=11)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"  Saved → {save_path}")


def plot_win_loss_rates(
    stats_list: list,
    save_path: str = 'win_loss_rates.png',
) -> None:
    """Grouped bar chart of win/loss/tie rates across all games."""
    games      = [s['game'] for s in stats_list]
    win_rates  = [s['win_rate']  * 100 for s in stats_list]
    loss_rates = [s['loss_rate'] * 100 for s in stats_list]
    tie_rates  = [s['tie_rate']  * 100 for s in stats_list]

    x     = np.arange(len(games))
    width = 0.26

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x - width, win_rates,  width, label='Win %',  color='#4CAF50', alpha=0.85)
    ax.bar(x,          loss_rates, width, label='Loss %', color='#F44336', alpha=0.85)
    ax.bar(x + width,  tie_rates,  width, label='Tie %',  color='#9E9E9E', alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(games, rotation=20, ha='right', fontsize=9)
    ax.set_ylabel('Percentage (%)', fontsize=11)
    ax.set_title('Win / Loss / Tie Rates — Monte Carlo Simulation', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"  Saved → {save_path}")


def plot_outcome_pie(
    df: pd.DataFrame,
    game_name: str,
    save_path: str = None,
) -> None:
    """Pie chart of outcome distribution for a single game."""
    if save_path is None:
        safe = game_name.lower().replace(' ', '_').replace("'", '').replace('(', '').replace(')', '')
        save_path = f'outcomes_{safe}.png'

    counts = df['outcome'].value_counts()
    color_map = {'win': '#4CAF50', 'loss': '#F44336', 'tie': '#9E9E9E'}
    colors = [color_map.get(l, '#2196F3') for l in counts.index]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts.values, labels=counts.index, autopct='%1.2f%%',
           colors=colors, startangle=140,
           wedgeprops={'edgecolor': 'white', 'linewidth': 1.2})
    ax.set_title(f'{game_name}\nOutcome Distribution', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"  Saved → {save_path}")


def plot_poker_hand_frequencies(
    series: pd.Series,
    save_path: str = 'poker_hand_frequencies.png',
) -> None:
    """Horizontal bar chart of Texas Hold'em hand frequencies."""
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.15, 0.85, len(series)))[::-1]
    bars = ax.barh(series.index, series.values, color=colors, edgecolor='white')

    for bar, val in zip(bars, series.values):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{val:.3f}%', va='center', fontsize=9)

    ax.set_xlabel('Frequency (%)', fontsize=11)
    ax.set_title("Texas Hold'em — Hand Category Frequencies\n(Monte Carlo)", fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"  Saved → {save_path}")


def plot_streak_distribution(
    streak_data: dict,
    game_name: str,
    save_path: str = None,
) -> None:
    """Bar chart of win-streak length distribution."""
    if save_path is None:
        safe = game_name.lower().replace(' ', '_').replace("'", '').replace('(', '').replace(')', '')
        save_path = f'streaks_{safe}.png'

    lengths = streak_data['streak_lengths']
    if not lengths:
        return
    counts = Counter(lengths)
    max_len = min(max(counts.keys()), 15)
    xs = list(range(1, max_len + 1))
    ys = [counts.get(x, 0) for x in xs]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(xs, ys, color='#2196F3', alpha=0.85, edgecolor='white')
    ax.set_xlabel('Streak Length (consecutive wins)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title(f'{game_name}\nWin Streak Length Distribution', fontsize=12, fontweight='bold')
    ax.set_xticks(xs)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"  Saved → {save_path}")


# keep Counter available for simulate_poker_hand_distribution
from collections import Counter
