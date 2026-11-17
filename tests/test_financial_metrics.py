"""Unit tests for deterministic financial calculations.

Every expected value is hand-computed so a passing suite proves formula correctness,
not agreement between two pieces of code.
"""

import pytest

from src.financial_metrics import (
    absolute_change,
    compute_all,
    current_ratio,
    debt_to_asset_ratio,
    net_margin,
    return_on_assets,
    yoy_growth,
)


# --- yoy_growth ---------------------------------------------------------
def test_yoy_growth_positive():
    assert yoy_growth(120, 100) == 20.0


def test_yoy_growth_negative():
    assert yoy_growth(80, 100) == -20.0


def test_yoy_growth_zero_base_returns_none():
    assert yoy_growth(100, 0) is None


def test_yoy_growth_negative_base_returns_none():
    assert yoy_growth(100, -5) is None


# --- net_margin ---------------------------------------------------------
def test_net_margin():
    # 96,995 / 383,285 = 25.306...%
    assert net_margin(96995, 383285) == 25.31


def test_net_margin_zero_revenue_raises():
    with pytest.raises(ValueError):
        net_margin(100, 0)


# --- debt_to_asset ------------------------------------------------------
def test_debt_to_asset_ratio():
    # 290,437 / 352,583 = 82.37%
    assert debt_to_asset_ratio(290437, 352583) == 82.37


# --- ROA ----------------------------------------------------------------
def test_return_on_assets():
    # 96,995 / 352,583 = 27.51%
    assert return_on_assets(96995, 352583) == 27.51


# --- current ratio ------------------------------------------------------
def test_current_ratio():
    # 143,566 / 145,308 = 0.99
    assert current_ratio(143566, 145308) == 0.99


def test_current_ratio_zero_liabilities_returns_none():
    assert current_ratio(100, 0) is None


# --- absolute change ----------------------------------------------------
def test_absolute_change():
    assert absolute_change(110543, 122151) == -11608


# --- compute_all integration -------------------------------------------
def test_compute_all_with_two_periods():
    data = {
        "FY2022": {
            "revenue": 394328, "net_income": 99803,
            "total_assets": 352755, "total_liabilities": 302083,
            "operating_cash_flow": 122151,
        },
        "FY2023": {
            "revenue": 383285, "net_income": 96995,
            "total_assets": 352583, "total_liabilities": 290437,
            "operating_cash_flow": 110543,
        },
    }
    result = compute_all(data)
    assert result["latest_period"] == "FY2023"
    assert result["prior_period"] == "FY2022"
    by_name = {m["name"]: m["value"] for m in result["metrics"]}
    # (383285-394328)/394328 = -2.80%
    assert by_name["Revenue YoY growth"] == -2.8
    assert by_name["Net margin"] == 25.31
    assert by_name["Debt-to-asset ratio"] == 82.37
    assert by_name["Operating cash flow change"] == -11608.0


def test_compute_all_graceful_on_missing_data():
    result = compute_all({"FY2023": {"revenue": 100}})
    assert result["metrics"] == []
    assert result["notes"]
