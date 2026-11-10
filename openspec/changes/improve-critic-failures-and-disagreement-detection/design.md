# Design

## Context

The graph fans out to three critic nodes, joins at `collect_critiques`, then calls `detect_disagreements` before conditional routing. `critiques` and `failed_critics` use additive reducers. Collection already counts dimensions and marks incomplete sets. Critic nodes already retry transient failures. The detector currently compares only whether critics have any issues, while `ConflictAssessment`, `DisagreementPrompts`, and tests for structured conflict responses exist but are unused. See `proposal.md` for motivation and the two capability specs for required behavior.

## Goals / Non-Goals

**Goals:**

- Keep the graph join and existing state contract intact while verifying complete, partial, and total critic failure outcomes.
- Derive adjudication solely from validated, explicit conflicts between available critics' issues.
- Retain the original critique objects so issue severity, including `critical`, stays available downstream.

**Non-Goals:**

- Add a general reliability score, recover failed critics beyond the existing retry loop, or create a verdict when evidence is incomplete.
- Implement adjudication or synthesis placeholders.

## Decisions

### Use the existing completeness signal for failure reliability

`collect_critiques` already returns `missing_dimensions`, `duplicate_dimensions`, and `critiques_complete`. Keep that signal as the authoritative distinction between complete and incomplete evidence. Verify that a single failure retains two critiques, and that total failure yields an empty critique list, all dimensions missing, `critiques_complete = False`, and no verdict from the current placeholder. Do not reinterpret `requires_adjudication` as a failure flag; it describes conflicts only. Alternative considered: route all failures to the adjudicator, but that placeholder cannot recover missing evidence and would conflate two different conditions.

### Compare explicit issue pairs from different critics

Build a stable indexed list of reported issues, retaining each issue's critic dimension and local issue number. If fewer than two distinct critics have issues, return no disagreements without invoking a model. Otherwise use the existing `DisagreementPrompts` and structured `ConflictAssessment` through the project's existing `ChatOpenAI` dependency to assess whether issue claims are incompatible. Pass the original question and generated answer for context, but accept conflicts only between explicit issue descriptions. Differences in score, confidence, severity, or issue presence are never candidates by themselves. Alternative considered: keyword matching, which cannot reliably distinguish semantic agreement from contradiction.

### Validate conflict references before routing

Ignore out-of-range indices, same-critic pairs, and duplicate or reversed pairs. Format retained conflicts with critic names and issue numbers so the reason for routing is inspectable. Set `requires_adjudication` from the validated disagreements list. Preserve the `critiques` reducer and original critiques; no new severity field is needed. If conflict assessment itself fails, let that error surface rather than return an empty list that falsely implies a completed comparison. Alternative considered: silently treating model failure as no conflict, which would misstate certainty.

## Risks / Trade-offs

- [Semantic judgment by a model may still miss or invent a conflict] → Keep the prompt narrow, validate references, and use deterministic mocked examples for compatible and incompatible claims.
- [Conflict assessment adds a model call when multiple critics have issues] → Skip the call unless at least two distinct critics reported issues; add no dependency.
- [The current synthesis node is a placeholder, so incomplete evidence has no final user-facing verdict policy] → Keep `critiques_complete` and `verdict` accurate; defer verdict policy to the later synthesis phase.

## Migration Plan

No data migration or interface change is required. Apply the detector change and focused tests together. Reverting that change restores the previous detector while leaving the state and graph contract intact.
