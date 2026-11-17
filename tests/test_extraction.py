"""Extraction tests against the real public filing and the golden dataset."""

import json
from pathlib import Path

import pytest

from src.document_reader import read_figures

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_data"
GOLDEN = json.loads((DATA / "golden_figures.json").read_text(encoding="utf-8"))
FY = GOLDEN["meta"]["filing"].split("September 30, ")[1][:4]
TARGET = f"FY{FY}"


@pytest.fixture(scope="module")
def figures():
    return read_figures(DATA / "apple_10k_2023.pdf")


def test_extracts_all_five_concepts(figures):
    concepts = {f.concept.value for f in figures}
    assert concepts == {
        "revenue", "net_income", "total_assets",
        "total_liabilities", "operating_cash_flow",
    }


def test_extracted_values_match_golden(figures):
    expected = GOLDEN["periods"][TARGET]
    by_concept = {f.concept.value: f.value for f in figures}
    for concept, value in expected.items():
        assert by_concept[concept] == pytest.approx(value), concept


def test_every_figure_has_page_evidence(figures):
    for f in figures:
        assert f.evidence.page is not None, f.concept
        assert f.evidence.snippet, f.concept
