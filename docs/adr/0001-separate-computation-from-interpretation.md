# ADR 0001 — Separate deterministic computation from LLM interpretation

- Status: Accepted
- Date: 2026-11-17
- Deciders: David Wu

## Context

Financial analysis requires exact arithmetic. Large language models are probabilistic
and can produce fluent but numerically false statements. A naive design that lets the
LLM both read figures and compute ratios would be simple to build but unsafe: a wrong
number presented confidently is worse than no number at all.

## Decision

Computation and interpretation are split into two isolated components:

- `financial_metrics.py` — pure functions, no I/O, no LLM. This is the only place a
  derived number is produced.
- `ai_analyst.py` — receives *only* already-verified figures and pre-computed metrics,
  and produces prose. It is forbidden from computing.

A third component, `hallucination_guard.py`, validates every numeric token in the AI
output against an allow-list built from verified data.

## Consequences

**Positive**

- Every derived number is reproducible and unit-testable.
- The primary failure mode (fabricated figures) is detectable and blocked.
- The LLM provider becomes swappable without touching numeric logic.

**Negative**

- More components and wiring than a single-prompt solution.
- The mock provider produces conservative, template-based prose until a real LLM is
  configured.

## Alternatives considered

- **Single LLM call for everything**: rejected — unverifiable arithmetic.
- **LLM computes, then a second LLM checks**: rejected — correlated errors; a checker
  with the same failure mode is not a real safeguard.
