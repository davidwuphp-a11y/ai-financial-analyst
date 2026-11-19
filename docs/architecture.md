# Architecture

## Overview

The system is a layered pipeline. **Numeric authority stays in the deterministic core.** The LLM receives verified figures and pre-computed metrics, returns prose, and does not supply facts or arithmetic.

```
Upload → Validate file → Ingest → Extract (+evidence) → Verify
       → Compute (pure functions) → Interpret (LLM) → Semantic guard → Report
```

## Modules

| Module | Responsibility | Key guarantee |
|---|---|---|
| `src/upload_security.py` | Size, signature, and XLSX container checks | Early rejection of malformed or oversized inputs; not malware scanning |
| `src/document_reader.py` | Read PDF/XLSX/CSV and locate figures | Evidence metadata attached at extraction time |
| `src/financial_metrics.py` | Pure functions for financial ratios | No I/O or LLM; deterministic calculations |
| `src/ai_analyst.py` | Provider-backed explanation | Mock by default; every generated claim passes through the semantic guard |
| `src/hallucination_guard.py` | Numeric allow-list and fact association checks | Blocks unverified numbers and explicit metric/value, period, unit, currency, and scale mismatches |
| `src/report_generator.py` | HTML/PDF output and evidence appendix | Escapes untrusted text before HTML insertion |
| `src/models.py` | Pydantic Figure, Metric, Evidence, and Claim contracts | Typed contracts between layers |
| `app.py` | Streamlit orchestration and UI | Thin presentation layer |

## Trust boundary

1. `financial_metrics.py` computes ratios using deterministic Python functions.
2. `ai_analyst.py` supplies the LLM only with extracted figures and pre-computed metrics.
3. `hallucination_guard.py` first checks numeric allow-list membership, then validates explicitly named facts against their own values and associated metadata.
4. `report_generator.py` includes only claims marked OK in the verified narrative section and escapes untrusted values in HTML output.

The semantic guard is deliberately rule-based. It is not a general-purpose natural-language parser and cannot prove causal statements or resolve every complex comparison.

## Data contracts

- **Figure:** concept, value, unit, scale, fiscal period, and evidence (document, page/sheet, snippet, confidence).
- **Metric:** name, value, unit, formula, inputs, and fiscal period.
- **Claim:** generated text, cited numeric tokens, status, and block reason.

## Evaluation and data provenance

- `evaluate.py` checks the included Apple FY2023 filing extraction fixture.
- `evaluate_benchmark.py` checks deterministic calculations against hand-checked FY2022–FY2023 values for Apple, Microsoft, and Amazon.
- The multi-company benchmark evaluates calculations, not multi-company PDF extraction. See [benchmark methodology](benchmark.md).

## Extension points

- Add a real LLM provider through environment variables; never hard-code credentials.
- Add financial metrics as pure functions with independent expected-value tests.
- Add issuer extraction support only with primary-source fixtures, page-level evidence, and documented limitations.
