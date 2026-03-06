from __future__ import annotations

from enum import StrEnum


class MetricType(StrEnum):
    ROAS = "ROAS"   # Return on Ad Spend = revenue / spend
    CTR = "CTR"     # Click-through Rate = clicks / impressions
    CPC = "CPC"     # Cost per Click = spend / clicks
    CPM = "CPM"     # Cost per Mille = spend / impressions * 1000
    CPA = "CPA"     # Cost per Acquisition = spend / conversions


class RuleOperator(StrEnum):
    LT = "LT"    # less than
    GT = "GT"    # greater than
    LTE = "LTE"  # less than or equal
    GTE = "GTE"  # greater than or equal
    EQ = "EQ"    # equal


class RuleAction(StrEnum):
    PAUSE_CAMPAIGN = "PAUSE_CAMPAIGN"
    REDUCE_BUDGET = "REDUCE_BUDGET"
    SEND_ALERT = "SEND_ALERT"
