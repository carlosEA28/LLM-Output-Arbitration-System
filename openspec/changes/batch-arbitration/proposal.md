# Proposal

## Why

Clients currently need one HTTP request per existing response they want to evaluate. A batch endpoint lets them submit several independent question and answer pairs in one request and receive each outcome even when another evaluation fails.

## What Changes

- Add `POST /v1/arbitrate/batch` for a nonempty list of items, each containing its own `original_question` and `generated_output`.
- Return one ordered result per item using the existing structured evaluation contract for successful items and a safe, item-specific failure status for unsuccessful items.
- Keep invalid batch input as a request-level validation error and preserve partial execution results when individual evaluations fail or time out.

## Capabilities

### New Capabilities

- `batch-arbitration`: Submission and independent reporting of multiple existing responses for arbitration through one API request.

### Modified Capabilities

None.

## Impact

The change affects FastAPI request and response schemas, the arbitration route, and focused API tests. It reuses `evaluate_response()` and the existing `EvaluationResponse` without changing the graph, critics, verdict semantics, `/evaluate`, generation, or persistence. No new dependency is expected.
