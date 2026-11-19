# Methodology

## 1. Financial formulas

All ratios are computed by pure functions in `src/financial_metrics.py`.

| Metric | Formula | Notes |
|---|---|---|
| Revenue YoY growth | `(rev_t − rev_{t−1}) / rev_{t−1} × 100` | Undefined if prior-period revenue ≤ 0 |
| Net margin | `net_income / revenue × 100` | Profitability |
| Debt-to-asset ratio | `total_liabilities / total_assets × 100` | Leverage |
| Operating cash flow | `ocf_t − ocf_{t−1}` and YoY % | Cash generation |
| Return on assets | `net_income / total_assets × 100` | Efficiency |
| Current ratio | `current_assets / current_liabilities` | Liquidity, when available |

Percentage functions return values such that `12.5` means 12.5%, rounded to two decimals.

## 2. Extraction approach

- PDF extraction uses line-oriented concept matching and is layout-sensitive.
- CSV/XLSX extraction expects structured rows and period columns.
- Every extracted `Figure` records a source document and page or sheet when available, plus a text snippet.
- Missing values are omitted rather than guessed.
- Upload checks reject oversized files, obvious extension/signature mismatches, malformed XLSX containers, and some archive-expansion risks. These checks do not replace parser isolation or malware scanning.

## 3. Evaluation datasets

### Single-filing extraction fixture

`data/sample_data/golden_figures.json` stores hand-checked Apple FY2022/FY2023 values. `evaluate.py` reports extraction matching, page evidence coverage, and injected numeric-fake blocking for the included filing only.

### Multi-company calculation benchmark

`data/benchmarks/multi_company_golden.json` contains Apple, Microsoft, and Amazon FY2022/FY2023 reference values and primary-source links. `evaluate_benchmark.py` compares four deterministic ratios against separately stored expected values.

This benchmark is not a multi-company extraction test. Microsoft's fiscal year ends June 30, while Apple and Amazon have different year-end dates. Amazon FY2023 total liabilities are derived from total assets less total stockholders' equity; the dataset discloses this derivation.

## 4. Numeric and semantic validation

The guard uses two layers:

1. Numeric allow-list membership: each numeric assertion must match a verified figure or computed metric within the configured rounding tolerance. Standalone four-digit fiscal-year labels are excluded from numeric assertions.
2. Fact association: explicitly named metrics and selected financial concepts are bound to their own verified values. The guard also checks explicit fiscal-year labels, percentage wording, currency markers, and scale wording where available.

A claim that fails validation is marked blocked and is not shown as a verified narrative claim in the final report. This is defense-in-depth, not proof of full semantic correctness; complex comparisons, implied periods, causal statements, and accounting-policy differences remain outside the guard's reliable scope.

## 5. Human review

Every extracted figure and generated narrative requires review against the original filing. The prototype is not investment advice, accounting advice, or a regulated financial service.
