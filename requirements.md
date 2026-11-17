# Requirements Specification — AI Financial Analyst

Version 1.0 · 2026-11-17 · Author: David Wu

## 1. Purpose

A prototype that reads public-company annual reports, extracts key financial figures,
computes financial ratios with **deterministic, unit-tested Python functions**, and
generates evidence-backed analysis with AI-assisted interpretation.

This is an experimental research prototype, **not** a regulated financial advisory
system. All AI-generated text requires human review.

## 2. Design principles (non-negotiable)

| # | Principle | Rationale |
|---|-----------|-----------|
| P1 | Arithmetic is never delegated to the LLM | LLMs hallucinate numbers; finance cannot tolerate this |
| P2 | Every figure is traceable to a source document + page | Auditability and user trust |
| P3 | AI output is validated against a numeric allow-list | A "hallucination guard" blocks figures the LLM invented |
| P4 | Calculations are pure functions with unit tests | Correctness is provable and reproducible |
| P5 | Public or synthetic data only | No confidential / internal material |

## 3. Functional requirements

| ID | Requirement | Acceptance criteria |
|----|-------------|---------------------|
| FR1 | Upload a financial report (PDF or XLSX/CSV) | File accepted; page/sheet count reported |
| FR2 | Extract revenue, net income, total assets, total liabilities, operating cash flow | Each figure carries value, unit, period, page, and raw text snippet |
| FR3 | Compute metrics by formula | YoY growth, net margin, debt-to-asset ratio, operating cash flow, plus ROA, current ratio — all via pure functions |
| FR4 | AI risk analysis | LLM explains *already-verified* figures; guard rejects any new numbers; mock provider is default |
| FR5 | Generate report | Downloadable HTML + PDF containing charts, metrics, evidence references, and disclaimer |

## 4. Non-functional requirements

- **Correctness**: 100% of metric unit tests pass; golden dataset figures match manually verified values.
- **Traceability**: ≥90% of extracted figures have a non-empty page reference.
- **Robustness**: Graceful errors for corrupt files, missing figures, invalid periods.
- **Reproducibility**: `pip install -r requirements.txt` then `streamlit run app.py` works from clean checkout.
- **Extensibility**: LLM provider is swappable via config (mock / OpenAI-compatible endpoint).

## 5. Data sources

- **Demo sample**: Apple Inc. Form 10-K, fiscal year ended September 30, 2023 (public SEC filing).
- **Unit tests**: synthetic figures with hand-computed expected values.
- Explicitly excluded: internal company files, client data, unpublished material.

## 6. Out of scope (v1)

- Reliable extraction from arbitrary/scanned real-world PDFs (documented limitation).
- Real LLM API calls (mock by default; provider interface ready).
- Regulatory compliance / investment advice.
