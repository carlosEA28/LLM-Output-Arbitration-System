# Proposal

## Why

The graph currently reaches empty adjudicator and verdict nodes, so neither route produces a usable assessment. Phase 3 must turn the existing critiques and disagreement signal into a structured final result, including when critic evidence is incomplete.

## What Changes

- Add a bounded verdict schema and the minimum schemas for dismissed issues and adjudication results.
- Implement the OpenAI adjudicator with dedicated prompts and Pydantic structured output to resolve supported conflicts and explain issue decisions without inventing evidence.
- Implement deterministic verdict synthesis for both graph routes, preserving available issues, reflecting partial failures in confidence, and marking total critic failure inconclusive.
- Add focused tests for the schemas, adjudicator, synthesis, and both graph routes. Correct the current disagreement detector only as needed to restore the already specified conflict routing behavior.

## Capabilities

### New Capabilities

- `issue-adjudication`: Resolve detected contradictions between available critic findings and record justified issue decisions.
- `verdict-synthesis`: Produce a bounded final assessment from available critiques and adjudication, including incomplete and inconclusive evidence.

### Modified Capabilities

None. No main specs currently exist; the earlier Phase 2 delta specs describe the intended disagreement behavior.

## Impact

This change affects the verdict schema, arbitration state, adjudicator prompt and node, verdict synthesis node, graph node bindings, and focused tests. It uses the existing OpenAI and Pydantic dependencies. It adds no API, UI, database, RAG, service, or new orchestration layer.
