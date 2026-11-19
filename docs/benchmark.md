# Multi-company benchmark methodology

## Purpose

The benchmark in `data/benchmarks/multi_company_golden.json` evaluates deterministic financial calculations against hand-checked reference values for three public companies across FY2022 and FY2023:

- Apple Inc.
- Microsoft Corporation
- Amazon.com, Inc.

It is a **calculation and semantic-validation benchmark**, not a multi-company PDF extraction benchmark. The PDF extraction test remains separately scoped to the included Apple FY2023 10-K fixture.

## Controls

1. All values use USD millions.
2. Fiscal-year labels and year-end conventions are retained as published; Microsoft's fiscal year ends June 30, while Apple and Amazon use September 30 and December 31 respectively.
3. Four metrics are compared to fixed expected values: revenue year-over-year growth, net margin, debt-to-asset ratio, and operating-cash-flow year-over-year growth.
4. Expected values are stored separately from the calculation code to avoid testing a function against itself.
5. Source links and data notes are stored with each company record.
6. Amazon FY2023 total liabilities are derived as total assets less total stockholders' equity because the consolidated balance sheet presents total liabilities and stockholders' equity as a combined total. This derivation is disclosed in the dataset metadata.

## Run

```bash
python evaluate_benchmark.py
pytest tests/test_benchmark.py -q
```

## Interpretation

A passing result establishes that the current deterministic functions reproduce the selected reference ratios for these three curated datasets. It does not establish extraction accuracy on unseen filings, accounting-policy comparability across issuers, suitability for investment decisions, or general semantic understanding by an LLM. The fiscal periods are not perfectly aligned by calendar year, so cross-company comparisons should account for each issuer's reporting calendar.
