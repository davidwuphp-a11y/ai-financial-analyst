"""Cross-company benchmark for deterministic financial calculations.

This benchmark checks arithmetic against hand-calculated expected values for three
public-company filings. It does not measure PDF extraction accuracy.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.financial_metrics import compute_all

DATA = Path(__file__).parent / "data" / "benchmarks" / "multi_company_golden.json"


def evaluate() -> dict:
    benchmark = json.loads(DATA.read_text(encoding="utf-8"))
    results = {}
    for company, record in benchmark["companies"].items():
        periods = record["periods"]
        computed = compute_all(periods)
        actual = {metric["name"]: metric["value"] for metric in computed["metrics"]}
        expected = record["expected_metrics_fy2023"]
        checks = {
            name: {
                "expected": value,
                "actual": actual.get(name),
                "passed": actual.get(name) == value,
            }
            for name, value in expected.items()
        }
        results[company] = {
            "periods": sorted(periods),
            "checks": checks,
            "passed": all(item["passed"] for item in checks.values()),
            "source": record["source"],
            "source_note": record["source_note"],
        }
    return {
        "benchmark": benchmark["benchmark_name"],
        "scope": benchmark["scope"],
        "company_count": len(results),
        "passed": all(result["passed"] for result in results.values()),
        "companies": results,
    }


def main() -> None:
    result = evaluate()
    print(f"Benchmark: {result['benchmark']}")
    print(f"Scope: {result['scope']}")
    print(f"Companies: {result['company_count']}")
    for company, record in result["companies"].items():
        status = "PASS" if record["passed"] else "FAIL"
        print(f"\n{company}: {status}")
        for name, check in record["checks"].items():
            print(f"  {name:<28} expected={check['expected']:>7.2f} actual={check['actual']!s:>7}")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
