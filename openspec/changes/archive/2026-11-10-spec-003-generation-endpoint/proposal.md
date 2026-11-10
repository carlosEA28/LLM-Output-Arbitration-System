# Proposal

## Why

Clients can currently evaluate an answer they already have, but cannot request the project's existing generate then evaluate flow through HTTP. Exposing that flow lets clients submit a question once and receive both the generated answer and its arbitration result.

## What Changes

- Add `POST /generate-and-evaluate` for a nonblank original question.
- Use the CLI's existing generator configuration to create the answer, then pass that answer through the existing evaluation service and graph.
- Return the generated answer alongside the existing structured evaluation fields.
- Add deterministic endpoint tests with controlled generation and evaluation results.

## Capabilities

### New Capabilities

- `api-generation`: Generate an answer and evaluate it through one HTTP request.

### Modified Capabilities

None. The existing `evaluation-reporting` capability covers offline runner reports and is unchanged.

## Impact

The change affects the FastAPI request, response, route, and service code, plus a small extraction of the CLI's current generation call for reuse. It preserves `POST /evaluate`, the CLI behavior, graph contracts, critic nodes, verdict semantics, and existing dependencies.
