# Limitations, validation scope, and roadmap

## Validation scope

The current evaluation is a reproducible demonstration against one public Apple Inc. FY2023 Form 10-K and a small set of unit tests. Results from this sample must not be generalized to arbitrary issuers, filing layouts, or financial statements.

## Known limitations

1. **Document layout:** PDF extraction matches selected statement labels and reads numeric tokens from nearby text lines. Multi-column statements, wrapped labels, footnotes, scanned documents, and issuer-specific layouts may fail or produce incomplete results.
2. **Semantic binding:** the numeric hallucination guard checks membership in a set of allowed numeric values. It does not bind a number to a specific metric, currency, scale, unit, or period. It can therefore miss a semantically incorrect reuse of an otherwise allowed number.
3. **Evidence quality:** page and snippet provenance improve traceability but do not independently establish that the extracted value is correct.
4. **LLM output:** model output can be incomplete, misleading, or contextually wrong even when all numeric tokens pass the current guard.
5. **Deployment:** the application is a single-user research prototype. It has not undergone a full security review, load test, or production deployment assessment.

## Recommended engineering roadmap

- Introduce typed financial facts that bind value + concept + period + currency + scale + unit + evidence.
- Validate claims against those typed facts rather than a global numeric allow-list.
- Add adversarial tests for negative values, percentages, currency symbols, scale conversions, repeated values, and period/metric swaps.
- Expand extraction fixtures across multiple issuers and statement layouts; add confidence scoring and human review for ambiguous results.
- Add file-size limits, per-upload temporary storage, and stricter MIME/content validation.
- Escape all untrusted content in generated HTML and add report-generation security tests.
- Add CI, dependency review, and a deployment threat model before hosting real user documents.

## Responsible use

Do not upload confidential, personal, material non-public, or restricted financial data. Outputs require qualified human review. The prototype is not investment advice, accounting advice, or a regulated financial service.
