"""
Central configuration for the semi-automated trading system.

Percentage values use decimal notation:
    0.002 = 0.20%
    0.02  = 2.00%
    0.10  = 10.00%
"""


# ============================================================
# EXECUTION
# ============================================================

EXECUTION_ENABLED = False


# ============================================================
# TRADE DIRECTION
# ============================================================

ALLOW_LONG_TRADES = True
ALLOW_SHORT_TRADES = False


# ============================================================
# TRADE QUALITY
# ============================================================

MINIMUM_TRADE_SCORE = 70.0


# ============================================================
# RISK MANAGEMENT
# ============================================================

RISK_PERCENT = 0.002
STOP_LOSS_PERCENT = 0.02
REWARD_RISK_RATIO = 2.0
MAX_POSITION_PERCENT = 0.10

MAX_DAILY_LOSS_PERCENT = 0.02
MAX_OPEN_TRADES = 1