# Proposal

## Why

The workflow already records critic failures, but its current disagreement detector treats an issue from one evaluation dimension and silence from another as a contradiction. This can send compatible assessments to adjudication and obscure what the available critiques actually support. Phase 2 needs explicit, tested behavior for partial and total failures and for genuine conflicts between critics.

## What Changes

- Specify and verify collection of three successful critiques, preservation of available critiques after one failure, and an incomplete result after all three fail.
- Compare explicit issue claims from different critics for incompatibility; differences in scores, issue counts, or evaluation dimensions alone will not create disagreements.
- Record only supported conflicts, request adjudication only for those conflicts, and retain critical issues in the critiques even when no conflict exists.
- Add deterministic tests using mocked critic and conflict-assessment model responses. Keep the existing retry policy, graph topology, state reducers, and Pydantic schemas where possible.

## Capabilities

### New Capabilities

- `critic-evaluation-collection`: Preserve parallel critic outcomes and report whether the expected evaluation dimensions are complete.
- `critic-disagreement-detection`: Identify substantive contradictions between explicit critic findings and determine when adjudication is warranted.

### Modified Capabilities

None; the project has no existing OpenSpec capability specs.

## Impact

The change affects `src/nodes/detect_disagreements.py`, its existing prompt and conflict schema, and tests for collection, failures, disagreement detection, and graph routing. `src/nodes/collect_critiques.py` and the graph may need only focused changes if the new tests expose a gap. No new dependencies or API, UI, RAG, adjudicator, or verdict synthesis work is planned.
