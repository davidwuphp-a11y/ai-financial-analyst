"""AI-assisted financial interpretation with a swappable provider.

The LLM interprets ONLY already-verified figures and metrics. It never computes.
The default provider is a deterministic mock so the project runs with zero API key
and zero cost. A real OpenAI-compatible endpoint can be enabled via environment
variables without changing any calling code.
"""

from __future__ import annotations

import os
from typing import Iterable

from .hallucination_guard import validate_all
from .models import Claim, Figure, Metric


SYSTEM_PROMPT = """You are a careful financial analyst assistant.
STRICT RULES:
1. Use ONLY the numbers provided in the context. Never invent, compute, or estimate a number.
2. Do not perform arithmetic. Refer to the pre-computed metrics by their given values.
3. Reference evidence by document and page when stated.
4. Be concise: 2-4 sentences per point. Flag anomalies cautiously as "may indicate".
5. If something looks unusual, say what could explain it and what to check next.
"""


def _context_block(figures: Iterable[Figure], metrics: Iterable[Metric]) -> str:
    lines = ["VERIFIED FIGURES (use these exact values only):"]
    for f in figures:
        lines.append(
            f"- {f.concept.value} {f.period} = {f.value:,.2f} {f.unit} "
            f"({f.scale}); source: {f.evidence.reference()}"
        )
    lines.append("VERIFIED METRICS (already computed; do not recompute):")
    for m in metrics:
        lines.append(f"- {m.name} ({m.period}) = {m.value} {m.unit}")
    return "\n".join(lines)


class MockProvider:
    """Deterministic, offline interpretation used by default."""

    def generate(self, context: str) -> list[str]:
        out: list[str] = []
        # Build statements strictly from values present in context.
        for line in context.splitlines():
            if line.startswith("- ") and "=" in line:
                label, value_part = line[2:].split("=", 1)
                value = value_part.strip().split()[0]
                label = label.strip()
                if "YoY growth" in label:
                    direction = "increased" if not value.startswith("-") else "declined"
                    out.append(
                        f"{label} {direction} to {value} percent in the latest period, "
                        f"a material movement worth reviewing against management discussion."
                    )
                elif "margin" in label.lower() or "return on" in label.lower():
                    out.append(
                        f"{label} stands at {value} percent, indicating the reported "
                        f"profitability level for the period."
                    )
                elif "Debt-to-asset" in label:
                    out.append(
                        f"{label} is {value} percent; leverage may warrant attention "
                        f"if it rises across periods."
                    )
        if not out:
            out.append("Verified data were loaded; limited metrics were available for narrative generation.")
        return out[:6]


class OpenAICompatibleProvider:
    """Optional real provider. Requires AI_API_KEY; uses chat-completions schema."""

    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or os.getenv("AI_MODEL", "gpt-4o-mini")
        self.base_url = base_url or os.getenv("AI_BASE_URL", "https://api.openai.com/v1")

    def generate(self, context: str) -> list[str]:
        from openai import OpenAI  # imported lazily; optional dependency

        client = OpenAI(api_key=os.environ["AI_API_KEY"], base_url=self.base_url)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context + "\n\nProvide 4 concise bullet points."},
            ],
            temperature=0,
        )
        content = resp.choices[0].message.content or ""
        return [ln.lstrip("-• ").strip() for ln in content.splitlines() if ln.strip()]


def get_provider() -> MockProvider | OpenAICompatibleProvider:
    provider = os.getenv("AI_PROVIDER", "mock").lower()
    if provider in {"openai", "compatible"}:
        return OpenAICompatibleProvider()
    return MockProvider()


def analyse(
    figures: Iterable[Figure],
    metrics: Iterable[Metric],
    provider=None,
) -> list[Claim]:
    """Generate and validate an AI narrative. Returns only allowed claims."""
    figures = list(figures)
    metrics = list(metrics)
    context = _context_block(figures, metrics)
    engine = provider or get_provider()
    raw_texts = engine.generate(context)

    trusted_values = [f.value for f in figures] + [m.value for m in metrics]
    claims = validate_all(raw_texts, trusted_values)
    return claims
