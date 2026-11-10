# Proposal

## Why

The FastAPI app currently exposes only a health check, so clients cannot submit an existing response for arbitration over HTTP. This change exposes the established graph through a small API adapter while preserving its evaluation contracts.

## What Changes

- Add `POST /evaluate` for an original question and an already-generated response.
- Invoke the existing arbitration graph through a thin service function.
- Return typed critiques, evaluation diagnostics, adjudication, and the graph's verdict as structured JSON.
- Add endpoint tests with controlled graph results and no model calls.

## Capabilities

### New Capabilities

- `api-arbitration`: HTTP submission and structured retrieval of an arbitration evaluation.

### Modified Capabilities

None.

## Impact

- Adds a route, a small service, and request/response transport schemas under `src/api/`; registers the route in `src/api/main.py`.
- Adds focused endpoint tests under `tests/`.
- Uses existing FastAPI, Pydantic, pytest, and graph dependencies; no new dependency is expected.
- Leaves graph, nodes, prompts, domain schemas, CLI, and evaluation runner unchanged.
