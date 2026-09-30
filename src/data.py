"""Shared loading and constants for the notebooks and the Streamlit app."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "processed" / "player_season.csv"

MV = "market_value_in_eur"
LOGMV = "log_market_value"
POS_ORDER = ["Goalkeeper", "Defender", "Midfield", "Attack"]
POS_COLORS = {"Goalkeeper": "#E69F00", "Defender": "#0072B2", "Midfield": "#009E73", "Attack": "#D55E00"}
AGE_GROUPS = ["Under 21", "21-23", "24-26", "27-29", "30+"]
MIN_MINUTES = 450

# sub-positions grouped for readable plots; Left/Right Midfield and Second Striker are too small (<300 rows)
SUBPOS_GROUP = {
    "Goalkeeper": "Goalkeeper", "Centre-Back": "Centre-Back", "Left-Back": "Full-Back", "Right-Back": "Full-Back",
    "Defensive Midfield": "Defensive Midfield", "Central Midfield": "Central Midfield",
    "Attacking Midfield": "Attacking Midfield", "Left Winger": "Winger", "Right Winger": "Winger",
    "Centre-Forward": "Centre-Forward",
}


def load_player_season(path=CSV):
    return pd.read_csv(path)


def eur(v):
    """1500000 -> '€1.5M', 350000 -> '€350K'."""
    if v >= 1e6:
        return f"€{v / 1e6:g}M"
    return f"€{v / 1e3:g}K"


def filter_data(df, seasons=None, leagues=None, positions=None, age_range=None, eligible_only=False):
    """Any filter left as None/empty-list-means-nothing-selected: an empty list returns an empty frame."""
    m = pd.Series(True, index=df.index)
    if seasons is not None:
        m &= df["season"].isin(seasons)
    if leagues is not None:
        m &= df["competition"].isin(leagues)
    if positions is not None:
        m &= df["position"].isin(positions)
    if age_range is not None:
        m &= df["age"].between(*age_range)
    if eligible_only:
        m &= df["analysis_minutes_eligible"]
    return df[m]


def season_label(s):
    return f"{s}/{str(s + 1)[2:]}"
