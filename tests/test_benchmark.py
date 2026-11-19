"""Regression tests for the sourced multi-company benchmark."""

from evaluate_benchmark import evaluate


def test_three_company_benchmark_passes():
    result = evaluate()
    assert result["company_count"] == 3
    assert result["passed"] is True
    assert set(result["companies"]) == {
        "Apple Inc.",
        "Microsoft Corporation",
        "Amazon.com, Inc.",
    }


def test_benchmark_discloses_its_scope_and_sources():
    result = evaluate()
    assert "not a multi-company document-extraction benchmark" in result["scope"]
    for company in result["companies"].values():
        assert company["source"].startswith("https://")
        assert company["source_note"]
