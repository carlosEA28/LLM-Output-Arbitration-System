# Tasks

## 1. Structured Results

- [x] 1.1 Add `DismissedIssueSchema`, `AdjudicationSchema`, and `VerdictSchema` in `src/arbitration/schemas/verdict.py`, reusing `IssueSchema`; verify Pydantic accepts valid values and rejects out-of-range scores, confidence, and empty dismissal reasons in focused tests.
- [x] 1.2 Type the adjudication and verdict fields in `ArbitrationState` without changing reducers; verify the schema and state imports load successfully.

## 2. Disagreement Routing

- [x] 2.1 Restore `detect_disagreements` to use its existing prompt and structured conflict schema for cross-critic issues, with validation of issue references; verify `tests/test_detect_disagreements.py` passes for compatible and contradictory findings.

## 3. Adjudicator

- [x] 3.1 Add dedicated system and user prompts in `src/prompts/adjudicator.py` using the existing prompt-class style; verify a focused test checks that question, response, critiques, disagreements, uncertainty, and evidence restrictions appear in the messages.
- [x] 3.2 Implement `src/nodes/adjudicator.py` with OpenAI structured output and grounded issue-decision validation; verify mocked tests cover confirmation, dismissal reasons, unmentioned issue preservation, and rejection of invented or contradictory decisions.

## 4. Verdict Synthesis

- [x] 4.1 Implement deterministic `src/nodes/synthesize_verdict.py` for adjudicated and direct routes, including issue preservation, score, coverage-based confidence, and inconclusive total failure; verify focused tests cover each case and schema validity.
- [x] 4.2 Bind the two real nodes in `graph.py` without changing edges or critic nodes; update existing graph assertions and verify mocked `tests/test_graph_routing.py` covers both paths and all-critic failure from START to END.
- [x] 4.3 Update the README's graph and verdict description to match the implemented behavior; verify the documented schema fields and limitations match the code.

## 5. Integration Check

- [x] 5.1 Run the full automated test suite and `openspec validate implement-adjudicator-and-verdict --strict`; verify the graph reaches END with a valid verdict on both conditional paths.
