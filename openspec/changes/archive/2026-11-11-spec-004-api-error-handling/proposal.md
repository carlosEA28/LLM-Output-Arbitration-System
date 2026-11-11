# Proposal

## Why

The API currently maps every execution failure to HTTP 500, including timeouts. Clients need a safe, explicit timeout response while retaining the existing distinction between a usable inconclusive verdict and an execution failure.

## What Changes

- Return a fixed HTTP 504 response when generation or arbitration propagates a timeout; keep other execution and invalid-result failures as fixed HTTP 500 responses.
- Keep HTTP 422 for invalid requests without starting generation or arbitration.
- Preserve HTTP 200 and the existing verdict and diagnostics for a graph result marked `inconclusive`.
- Ensure failure responses omit exception messages, provider traces, credentials, prompts, and model payloads.

## Capabilities

### New Capabilities

- `api-error-handling`: Safe execution-failure and timeout behavior for the arbitration API endpoints.

### Modified Capabilities

- `api-generation`: Distinguish propagated timeouts from other generation or arbitration failures on `POST /generate-and-evaluate`.

## Impact

The existing API routes and, only if needed, their small service boundary and focused endpoint tests. The graph, CLI, evaluation runner, provider configuration, and dependency set remain unchanged.
