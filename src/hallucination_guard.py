"""Numeric hallucination guard — defense-in-depth for AI-generated text.

Even when the LLM is told to use only provided figures, it may emit numbers it
invented. This module extracts every numeric token from the narrative and checks it
against an allow-list derived from verified figures and computed metrics. Claims that
contain unauthorised numbers are marked BLOCKED and excluded from the final report.
"""

from __future__ import annotations

import re
from typing import Iterable

from .models import Claim, ClaimStatus

NUM_TOKEN_RE = re.compile(r"-?\d[\d,]*\.?\d*\s*%?")


def build_allow_list(values: Iterable[float]) -> set[str]:
    """Normalise trusted numbers into comparable string forms.

    We include the value with 0, 1 and 2 decimal places, plus the integer form, so a
    metric of 12.34 is not falsely blocked when written as "12.3" or "12".
    """
    allowed: set[str] = set()
    for v in values:
        for decimals in (0, 1, 2):
            allowed.add(f"{round(v, decimals):.{decimals}f}")
        allowed.add(f"{int(round(v)):,}")
    return allowed


def _numeric_tokens(text: str) -> list[str]:
    # A 4-digit calendar year (e.g. FY2023) is a period label, not a financial
    # assertion, so it is not subject to the allow-list check.
    return [
        t.strip() for t in NUM_TOKEN_RE.findall(text)
        if not re.fullmatch(r"(19|20)\d{2}\s*%?", t.strip())
    ]


def _token_is_allowed(token: str, allowed: set[str]) -> bool:
    stripped = token.replace("%", "").replace(",", "").strip()
    try:
        num = float(stripped)
    except ValueError:
        return False
    for decimals in (0, 1, 2):
        if f"{round(num, decimals):.{decimals}f}" in allowed:
            return True
    if f"{int(round(num)):,}" in allowed:
        return True
    return False


def validate_claim(text: str, allowed: set[str]) -> Claim:
    """Validate a single narrative claim; return it with ok/blocked status."""
    bad = [t for t in _numeric_tokens(text) if not _token_is_allowed(t, allowed)]
    if bad:
        return Claim(
            text=text,
            status=ClaimStatus.BLOCKED,
            reason=f"Unverified number(s) detected: {', '.join(bad)}",
        )
    return Claim(text=text, cited_figures=_numeric_tokens(text), status=ClaimStatus.OK)


def validate_all(texts: Iterable[str], allowed_values: Iterable[float]) -> list[Claim]:
    """Validate a batch of claims against a set of trusted numeric values."""
    allowed = build_allow_list(allowed_values)
    return [validate_claim(t, allowed) for t in texts]
