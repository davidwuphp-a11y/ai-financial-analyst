# Methodology

## 1. Financial formulas

All ratios are computed by pure functions in `src/financial_metrics.py`.
Units are consistent (figures are normalised to the reported unit before computation).

| Metric | Formula | Notes |
|--------|---------|-------|
| Revenue YoY growth | `(rev_t − rev_{t−1}) / rev_{t−1} × 100` | Undefined if prior ≤ 0 |
| Net margin | `net_income / revenue × 100` | Profitability |
| Debt-to-asset ratio | `total_liabilities / total_assets × 100` | Leverage |
| Operating cash flow | `ocf_t − ocf_{t−1}` (absolute) and YoY % | Cash generation |
| Return on assets (ROA) | `net_income / total_assets × 100` | Efficiency |
| Current ratio | `current_assets / current_liabilities` | Liquidity (when available) |

Percentages are returned as numbers (e.g. `12.5` means 12.5%) and rounded to 2 decimals
only at presentation time, never before further computation.

## 2. Extraction approach

- **Primary source**: the downloaded Apple FY2023 Form 10-K (SEC public filing).
- Figures are located by concept labels (e.g. "Total net sales", "Net income") and the
  nearest numeric token in the same row/column, using pdfplumber word coordinates.
- Each extracted `Figure` records the exact page number and the raw text line, so a user
  can verify the value against the source.
- When a figure cannot be found, the system returns "not found" — **it never guesses**.

## 3. Golden dataset

A hand-verified reference set (`data/sample_data/golden_figures.json`) stores the expected
values for the demo filing. The evaluation harness compares extraction output against
it and reports:

- **Extraction accuracy**: share of figures matched to the golden value.
- **Evidence coverage**: share of figures with a non-empty page reference.
- **Hallucination block rate**: share of injected fake numbers caught by the guard.

## 4. Hallucination guard

The LLM is prompted with `EVIDENCE_MODE`: it must only use numbers present in the
provided verified context. After generation, a regex scan extracts every numeric token;
each token is checked against the allow-list (verified figures + computed metrics ±
tolerance). Any unauthorised number marks the claim `blocked` and it is removed from the
final report. This is defense-in-depth: prompt constraint + post-hoc validation.

## 5. Limitations

- Extraction is tuned for the demo filing's layout. Arbitrary or scanned PDFs are not
  reliably supported in v1 — this is stated honestly rather than concealed.
- The default AI provider is a mock. Real interpretation requires an API key.
- This tool does not provide investment advice and outputs require human review.
