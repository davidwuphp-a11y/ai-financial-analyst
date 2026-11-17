# Architecture

## Overview

The system is a layered pipeline. Information flows downward; **numeric authority flows
only through the deterministic core**. The LLM sits in a side position: it receives
verified numbers and returns prose, never figures that are trusted as facts.

```
Upload → Ingest → Extract (+evidence) → Verify → Compute (pure) → Interpret (LLM) → Guard → Report
                                                        │                            │
                                                   unit tests              numeric allow-list
```

## Modules

| Module | Responsibility | Key guarantee |
|--------|----------------|---------------|
| `src/document_reader.py` | Read PDF/XLSX/CSV; locate figures with page + snippet | Evidence metadata attached at extraction time |
| `src/financial_metrics.py` | Pure functions for every ratio | No I/O, no LLM, fully unit-tested |
| `src/ai_analyst.py` | LLM-backed explanation, configurable provider | Mock by default; returns structured claims |
| `src/hallucination_guard.py` | Validate every number in AI text against allow-list | Blocks unauthorised figures |
| `src/report_generator.py` | Render HTML + PDF with charts and evidence | Deterministic export |
| `src/models.py` | Pydantic schemas (Figure, Metric, Evidence, Claims) | Type-safe contracts between layers |
| `app.py` | Streamlit UI orchestrating the pipeline | Thin layer; no business logic |

## The trust boundary (why this matters)

The central design decision is a **separation of concerns between computation and
interpretation**:

1. `financial_metrics.py` computes numbers. Its functions are deterministic and tested.
2. `ai_analyst.py` may only *narrate* those numbers. It is given the verified set.
3. `hallucination_guard.py` scans the narrative. Any numeric token not present in the
   verified set (within tolerance) is flagged and the claim is dropped or rewritten.

This directly addresses the primary failure mode of LLM-based financial tools —
confidently stated wrong numbers — and is why the project is more than a CRUD demo.

## Data flow contracts

- **Figure**: `{concept, value, unit, period, document, page, snippet, confidence}`
- **Metric**: `{name, value, formula, inputs, period}`
- **Claim**: `{text, cited_figures, status}` where status ∈ {ok, blocked}

## Extension points

- Add a real LLM: set `AI_PROVIDER=openai` and provide `AI_API_KEY` env var.
- Add new ratios: add a pure function + a unit test in `financial_metrics.py`.
- Add new filings: drop the PDF into `data/sample_data/`.
