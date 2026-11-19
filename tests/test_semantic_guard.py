"""Regression tests for semantic financial-claim validation."""

from src.ai_analyst import analyse
from src.hallucination_guard import validate_claim_against_facts
from src.models import Concept, Evidence, Figure, Metric, ClaimStatus


def _facts():
    figure = Figure(
        concept=Concept.REVENUE,
        value=383285,
        unit="USD",
        scale="millions",
        period="FY2023",
        evidence=Evidence(document="sample.pdf", page=1),
    )
    margin = Metric(
        name="Net margin",
        value=25.31,
        unit="percent",
        formula="net income / revenue x 100",
        inputs={"net_income": 96995, "revenue": 383285},
        period="FY2023",
    )
    return [figure], [margin]


def test_metric_must_use_its_own_verified_value():
    figures, metrics = _facts()
    claim = validate_claim_against_facts(
        "Net margin was 82.37 percent in FY2023.", figures, metrics
    )
    assert claim.status == ClaimStatus.BLOCKED
    assert "Semantic mismatch" in claim.reason


def test_metric_must_use_percentage_unit():
    figures, metrics = _facts()
    claim = validate_claim_against_facts(
        "Net margin was 25.31 in FY2023.", figures, metrics
    )
    assert claim.status == ClaimStatus.BLOCKED
    assert "Unit mismatch" in claim.reason


def test_metric_period_must_match():
    figures, metrics = _facts()
    claim = validate_claim_against_facts(
        "Net margin was 25.31 percent in FY2022.", figures, metrics
    )
    assert claim.status == ClaimStatus.BLOCKED
    assert "Period mismatch" in claim.reason


def test_figure_currency_must_match():
    figures, metrics = _facts()
    claim = validate_claim_against_facts(
        "Revenue was 383,285 million CNY in FY2023.", figures, metrics
    )
    assert claim.status == ClaimStatus.BLOCKED
    assert "Currency mismatch" in claim.reason


def test_figure_scale_must_match():
    figures, metrics = _facts()
    claim = validate_claim_against_facts(
        "Revenue was 383,285 billion USD in FY2023.", figures, metrics
    )
    assert claim.status == ClaimStatus.BLOCKED
    assert "Scale mismatch" in claim.reason


def test_correct_claim_passes():
    figures, metrics = _facts()
    claim = validate_claim_against_facts(
        "Revenue was 383,285 million USD in FY2023.", figures, metrics
    )
    assert claim.status == ClaimStatus.OK


def test_analysis_pipeline_uses_semantic_validation():
    figures, metrics = _facts()

    class Provider:
        def generate(self, context):
            return [
                "Net margin was 25.31 percent in FY2023.",
                "Net margin was 82.37 percent in FY2023.",
            ]

    claims = analyse(figures, metrics, provider=Provider())
    assert [claim.status for claim in claims] == [ClaimStatus.OK, ClaimStatus.BLOCKED]
