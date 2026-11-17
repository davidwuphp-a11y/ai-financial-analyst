"""Tests for the numeric hallucination guard."""

from src.hallucination_guard import build_allow_list, validate_all, validate_claim


def test_allowed_number_passes():
    allowed = build_allow_list([383285, 25.31, -2.8])
    claim = validate_claim("Revenue reached 383,285 million this year.", allowed)
    assert claim.status.value == "ok"


def test_invented_number_is_blocked():
    allowed = build_allow_list([383285, 25.31])
    claim = validate_claim("Revenue reached 999,999 million this year.", allowed)
    assert claim.status.value == "blocked"
    assert "999,999" in claim.reason


def test_mixed_claim_blocked_but_flagged():
    allowed = build_allow_list([100, 25.0])
    claims = validate_all(
        ["Margin was 25.0 percent.", "Growth hit 77 percent unexpectedly."],
        [100, 25.0],
    )
    assert claims[0].status.value == "ok"
    assert claims[1].status.value == "blocked"


def test_guard_tolerates_rounding():
    allowed = build_allow_list([12.34])
    assert validate_claim("Value about 12.3 percent", allowed).status.value == "ok"
