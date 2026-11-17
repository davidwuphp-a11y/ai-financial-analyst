"""Reproducible evaluation harness.

Runs the pipeline against the golden dataset and prints a benchmark table:
  - extraction accuracy vs hand-verified figures
  - evidence coverage (page references present)
  - hallucination block rate on injected fake numbers

Run: python evaluate.py
"""

from __future__ import annotations

import json
from pathlib import Path

from src.ai_analyst import analyse
from src.document_reader import read_figures
from src.financial_metrics import compute_all
from src.hallucination_guard import validate_all
from src.models import Metric

DATA = Path(__file__).parent / "data" / "sample_data"


def main() -> None:
    golden = json.loads((DATA / "golden_figures.json").read_text(encoding="utf-8"))
    figures = read_figures(DATA / "apple_10k_2023.pdf")
    fy = golden["meta"]["filing"].split("September 30, ")[1][:4]
    target = f"FY{fy}"

    expected = golden["periods"][target]
    by_concept = {f.concept.value: f.value for f in figures}

    matched = sum(
        1 for c, v in expected.items()
        if c in by_concept and abs(by_concept[c] - v) < 0.5
    )
    accuracy = matched / len(expected) * 100

    evidenced = sum(1 for f in figures if f.evidence.page is not None)
    coverage = evidenced / len(figures) * 100 if figures else 0.0

    # Hallucination test: mix real numbers with injected fakes.
    real = list(expected.values())
    fakes = [1234567, 88.88, 654321]
    test_texts = [f"Figure was {v:,.0f} million." for v in real + fakes]
    validated = validate_all(test_texts, real)
    blocked = sum(1 for c in validated if c.status.value == "blocked")
    block_rate = blocked / len(fakes) * 100

    periods = {
        p: {k: float(v) for k, v in vals.items()}
        for p, vals in golden["periods"].items()
    }
    result = compute_all(periods)
    metric_lines = "\n".join(
        f"  {m['name']:<28} {m['value']:>10,.2f} {m['unit']}" for m in result["metrics"]
    )

    print("=" * 62)
    print("  AI FINANCIAL ANALYST - EVALUATION BENCHMARK")
    print("=" * 62)
    print(f"  Company          : {golden['meta']['company']}")
    print(f"  Filing           : {golden['meta']['filing']}")
    print("-" * 62)
    print(f"  Extraction accuracy     : {accuracy:>6.1f}%  ({matched}/{len(expected)})")
    print(f"  Evidence coverage       : {coverage:>6.1f}%  ({evidenced}/{len(figures)})")
    print(f"  Hallucination block rate: {block_rate:>6.1f}%  ({blocked}/{len(fakes)} fakes caught)")
    print("-" * 62)
    print("  Computed metrics (deterministic):")
    print(metric_lines)
    print("=" * 62)


if __name__ == "__main__":
    main()
