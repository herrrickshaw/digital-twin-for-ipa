"""Paths and constants shared by the reportage modules."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.expanduser("~/india-trade-sector-policy-recommendations/data/pib_index.sqlite")
CAP_PER_QUARTER = 30
STATE_DB = os.path.join(ROOT, "data/registers/state_news.sqlite")


def quarter_of(datestr):
    y, mth = int(datestr[:4]), int(datestr[5:7])
    return f"{y}Q{(mth - 1) // 3 + 1}"
