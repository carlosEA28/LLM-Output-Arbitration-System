# Design

## Context

See `proposal.md` for motivation and the two delta specs for behavior. `ArbitrationState` already accumulates critiques and failures; `collect_critiques` reports missing and duplicate dimensions. The graph already forks three critics, routes on `requires_adjudication`, and rejoins at synthesis. `graph.py` contains the two empty node functions, and `verdict.py` is empty. The checked-in `detect_disagreements.py` currently checks score/issue consistency instead of the cross-critic conflicts described by its existing prompt, conflict schema, tests, and Phase 2 delta spec.

## Goals / Non-Goals

**Goals:**

- Fill the existing two nodes with narrow implementations and preserve the current graph topology and reducers.
- Keep issue decisions traceable to supplied `IssueSchema` values and keep synthesis deterministic.
- Make evidence coverage and an all-critic failure visible in the verdict.

**Non-Goals:**

- Independently verify factual claims, calibrate model confidence, or change critic scoring and retry behavior.
- Add another provider, external source, synthesis LLM call, or new graph layer.

## Decisions

### Structured data and state

Define `DismissedIssueSchema` with an `IssueSchema` and nonempty `reason`, `AdjudicationSchema` with `confirmed_issues: list[IssueSchema]` and `dismissed_issues: list[DismissedIssueSchema]`, and `VerdictSchema` with the requested five fields plus `status: Literal["assessed", "inconclusive"]`. Use Pydantic bounds matching existing schemas. Change `ArbitrationState.verdict` to `VerdictSchema | None` and add one optional adjudication field. No reducer is needed for either field because only one node writes each. An explicit status is necessary because the required integer score cannot itself represent inconclusive evidence. Alternative: make the score nullable, which conflicts with the requested schema.

### Adjudication

Put the implementation in `src/nodes/adjudicator.py` and bind it in `graph.py`. `AdjudicatorPrompts` in `src/prompts/adjudicator.py` supplies a system prompt and a user prompt containing the original question, response, available critiques, and disagreement strings. Follow the existing `ChatOpenAI(...).with_structured_output(AdjudicationSchema).invoke([SystemMessage, HumanMessage])` pattern, using the already installed OpenAI integration. The prompt asks for decisions only about supplied issues, treats dimension differences as compatible unless claims truly conflict, and states uncertainty where facts are unverified. Validate returned issues against the supplied `IssueSchema` values and reject fabricated or contradictory decisions; preserve issues that are not explicitly dismissed. Return only `{"adjudication": result}`. Model failures surface as errors, as disagreement-assessment failures currently do. Alternative: silently accept ungrounded model output, which could remove legitimate issues or add unsupported claims.

### Verdict synthesis

Put a pure synthesis function in `src/nodes/synthesize_verdict.py`, bound by the existing graph. Start with all critic issues in stable critique order; exclude only issues explicitly dismissed by a valid adjudication, retain all others, and carry dismissal reasons into the verdict. When there is no adjudication, all available issues remain confirmed. De-duplicate identical issue values in the final lists to avoid repeated findings. Compute the score from the arithmetic mean of one available critique score per dimension, mapped linearly from 1–5 to 1–10 and rounded to the nearest integer; this is a descriptive score, not a verified correctness measure. Use a fixed coverage heuristic for confidence: `0.75 * unique_dimensions / 3`, capped at `0.5` when failures or duplicate dimensions are recorded. Do not use critics' self-reported confidence as a calibrated probability. The summary states issue counts and evidence coverage, including lack of independent factual verification. With zero critiques, return `status="inconclusive"`, `overall_score=1` as a sentinel, `confidence=0`, empty issue lists, and a summary explaining that no assessment was possible. Alternative: another model call for synthesis, which would add variability without needed information.

### Existing disagreement behavior

Make only the focused correction needed for the existing detector to use its `DisagreementPrompts` and `ConflictAssessment`: compare issues from at least two critics, accept only valid cross-critic issue pairs, and derive `requires_adjudication` from the accepted conflicts. This restores the behavior already specified in the Phase 2 delta and covered by existing tests. Leave critic nodes, reducers, and graph edges intact. Alternative: route every score difference to adjudication, which would conflate independent dimensions.

## Risks / Trade-offs

- [Model adjudication may assert an unsupported factual conclusion] → Prompt for uncertainty and validate issue identity; the verdict summary says factual claims were not independently verified.
- [A dismissed issue may still influence a critic's numeric score] → Keep score calculation simple and label it as derived from critic ratings; adjudication controls the issue lists, not historical critic scores.
- [The required score on total failure can look like a quality judgment] → Add `inconclusive` status, zero confidence, and an explicit sentinel explanation.
- [Duplicate dimensions may skew a score] → Use one score per dimension and lower confidence while preserving all issue findings.

## Migration Plan

No data migration is needed. The graph's returned `verdict` changes from `str | None` to `VerdictSchema | None`; callers should read the structured fields. Existing tests that assert `None` after a successful graph run must be updated to assert a verdict. Rollback is limited to reverting these code changes.
