"""Security regression tests for HTML report rendering."""

from src.models import Claim, ClaimStatus, Evidence, Figure, Concept, Metric
from src.report_generator import build_html_report


def test_report_escapes_untrusted_html_fields():
    figure = Figure(
        concept=Concept.REVENUE,
        value=1234,
        period="FY2024",
        evidence=Evidence(
            document="<script>alert(1)</script>",
            page=1,
            snippet="<img src=x onerror=alert(1)>",
        ),
    )
    metric = Metric(
        name="<svg onload=alert(1)>",
        value=12.5,
        unit="percent",
        formula="<script>alert(2)</script>",
        inputs={},
        period="FY2024",
    )
    claim = Claim(
        text="<script>alert(3)</script>",
        status=ClaimStatus.OK,
    )

    report = build_html_report(
        [figure],
        [metric],
        [claim],
        company="<iframe src=evil></iframe>",
    )

    assert "<script>alert(1)</script>" not in report
    assert "<img src=x onerror=alert(1)>" not in report
    assert "<svg onload=alert(1)>" not in report
    assert "<script>alert(2)</script>" not in report
    assert "<script>alert(3)</script>" not in report
    assert "<iframe src=evil>" not in report
    assert "&lt;script&gt;" in report
