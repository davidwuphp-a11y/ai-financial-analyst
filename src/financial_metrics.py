"""Deterministic financial calculations.

DESIGN RULE: this module contains ONLY pure functions. No LLM, no file I/O, no
randomness. Every number a user trusts as a fact originates here. Keeping arithmetic out
of the language model is the single most important correctness decision in the project.

All percentage functions return a number such that 12.5 means 12.5%.
"""

from __future__ import annotations

from typing import Optional


def _require_positive(value: float, name: str) -> None:
    if value is None or value <= 0:
        raise ValueError(f"{name} must be a positive number, got {value!r}")


def yoy_growth(current: float, previous: float) -> Optional[float]:
    """Year-over-year growth rate in percent.

    (current - previous) / previous * 100
    Returns None when the base is non-positive (growth undefined).
    """
    if previous is None or previous <= 0:
        return None
    return round((current - previous) / previous * 100, 2)


def net_margin(net_income: float, revenue: float) -> Optional[float]:
    """Net income as a percentage of revenue."""
    _require_positive(revenue, "revenue")
    return round(net_income / revenue * 100, 2)


def debt_to_asset_ratio(total_liabilities: float, total_assets: float) -> Optional[float]:
    """Total liabilities as a percentage of total assets (leverage)."""
    _require_positive(total_assets, "total_assets")
    return round(total_liabilities / total_assets * 100, 2)


def return_on_assets(net_income: float, total_assets: float) -> Optional[float]:
    """Net income as a percentage of total assets."""
    _require_positive(total_assets, "total_assets")
    return round(net_income / total_assets * 100, 2)


def current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
    """Liquidity ratio. Returns None when liabilities are non-positive."""
    if current_liabilities is None or current_liabilities <= 0:
        return None
    return round(current_assets / current_liabilities, 2)


def absolute_change(current: float, previous: float) -> float:
    """Simple absolute difference between two periods."""
    return round(current - previous, 2)


def compute_all(figures_by_period: dict[str, dict[str, float]]) -> dict:
    """Compute the standard metric set from a mapping of period -> {concept: value}.

    Example input:
        {
          "FY2023": {"revenue": 383285, "net_income": 96995, ...},
          "FY2022": {"revenue": 394328, "net_income": 99803, ...},
        }
    Missing concepts are skipped with an explanatory note rather than raising, so the
    UI can still render a partial analysis honestly.
    """
    periods = sorted(figures_by_period.keys())
    if not periods:
        return {"metrics": [], "notes": ["No periods supplied."]}

    latest = periods[-1]
    prior = periods[-2] if len(periods) >= 2 else None
    cur = figures_by_period[latest]
    prev = figures_by_period.get(prior, {}) if prior else {}
    metrics: list[dict] = []
    notes: list[str] = []

    def add(name, value, unit, formula, inputs):
        if value is not None:
            metrics.append({
                "name": name, "value": value, "unit": unit,
                "formula": formula, "inputs": inputs, "period": latest,
            })

    rev_c, rev_p = cur.get("revenue"), prev.get("revenue")
    if rev_c is not None and rev_p is not None:
        add("Revenue YoY growth", yoy_growth(rev_c, rev_p), "percent",
            "(revenue_t - revenue_t-1) / revenue_t-1 x 100",
            {"revenue_t": rev_c, "revenue_t-1": rev_p})
    else:
        notes.append("Revenue YoY growth skipped: revenue missing in one or both periods.")

    ni, rv = cur.get("net_income"), cur.get("revenue")
    if ni is not None and rv:
        add("Net margin", net_margin(ni, rv), "percent",
            "net_income / revenue x 100", {"net_income": ni, "revenue": rv})

    tl, ta = cur.get("total_liabilities"), cur.get("total_assets")
    if tl is not None and ta:
        add("Debt-to-asset ratio", debt_to_asset_ratio(tl, ta), "percent",
            "total_liabilities / total_assets x 100",
            {"total_liabilities": tl, "total_assets": ta})

    if ni is not None and ta:
        add("Return on assets", return_on_assets(ni, ta), "percent",
            "net_income / total_assets x 100", {"net_income": ni, "total_assets": ta})

    ocf_c, ocf_p = cur.get("operating_cash_flow"), prev.get("operating_cash_flow")
    if ocf_c is not None and ocf_p is not None:
        add("Operating cash flow YoY", yoy_growth(ocf_c, ocf_p), "percent",
            "(ocf_t - ocf_t-1) / ocf_t-1 x 100",
            {"ocf_t": ocf_c, "ocf_t-1": ocf_p})
        add("Operating cash flow change", absolute_change(ocf_c, ocf_p), "currency",
            "ocf_t - ocf_t-1", {"ocf_t": ocf_c, "ocf_t-1": ocf_p})

    ca, cl = cur.get("current_assets"), cur.get("current_liabilities")
    if ca is not None and cl:
        add("Current ratio", current_ratio(ca, cl), "ratio",
            "current_assets / current_liabilities",
            {"current_assets": ca, "current_liabilities": cl})

    return {"latest_period": latest, "prior_period": prior, "metrics": metrics, "notes": notes}
