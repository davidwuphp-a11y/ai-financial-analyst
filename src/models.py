"""Typed data contracts shared across the pipeline.

Every figure that leaves the extraction layer carries evidence metadata. This is what
makes the "traceability" guarantee enforceable rather than aspirational.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Concept(str, Enum):
    """Canonical financial concepts the prototype recognises."""

    REVENUE = "revenue"
    NET_INCOME = "net_income"
    TOTAL_ASSETS = "total_assets"
    TOTAL_LIABILITIES = "total_liabilities"
    OPERATING_CASH_FLOW = "operating_cash_flow"


class Evidence(BaseModel):
    """Where a figure came from — the audit trail."""

    document: str
    page: int | None = None
    sheet: str | None = None
    snippet: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    def reference(self) -> str:
        if self.page is not None:
            return f"{self.document}, p.{self.page}"
        if self.sheet is not None:
            return f"{self.document}, sheet '{self.sheet}'"
        return self.document


class Figure(BaseModel):
    """A single extracted, evidenced financial value."""

    concept: Concept
    value: float
    unit: str = "USD"
    scale: str = "millions"          # reported scale, e.g. "thousands"/"millions"
    period: str                       # e.g. "FY2023"
    evidence: Evidence


class Metric(BaseModel):
    """A deterministic computed ratio."""

    name: str
    value: float
    unit: Literal["percent", "ratio", "currency"] = "percent"
    formula: str
    inputs: dict[str, float]
    period: str


class ClaimStatus(str, Enum):
    OK = "ok"
    BLOCKED = "blocked"


class Claim(BaseModel):
    """An AI-generated sentence plus its validation status."""

    text: str
    cited_figures: list[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.OK
    reason: str = ""
