# Monte Carlo Card Game Simulator

A Python project that uses Monte Carlo simulation to analyze probabilities and win rates across multiple card games including Blackjack, Baccarat, and Poker.

## Overview

This project simulates thousands of card game hands to calculate real win rates and probabilities using the Monte Carlo method. Instead of relying on theoretical odds, the simulator runs large numbers of random simulations to estimate outcomes empirically.

## Games

- **Blackjack** — simulate thousands of hands and track win/loss rates over time
- **Baccarat** — simulate player vs banker outcomes across large sample sizes
- **Poker** — simulate hand strength probabilities and win rates

## How it works

Monte Carlo simulation works by running a random process thousands of times and observing the outcomes. In this project, each card game is simulated thousands of times and the results are aggregated to estimate:

- Win rate percentage
- Bankroll change over time
- Probability of winning N hands in a row

## Project Structure

```
monte_carlo/
│
├── src/
│   ├── __init__.py
│   ├── simulation.py      # core deck and card logic
│   └── analysis.py        # stats, win rates, and visualization
│
├── tests/
│   └── test_simulation.py
│
├── requirements.txt
├── README.md
└── main.py
```

## Setup

Clone the repository and set up a virtual environment:

```
git clone <repo-url>
cd monte_carlo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```
python main.py
```

## Dependencies

- numpy
- pandas
- matplotlib