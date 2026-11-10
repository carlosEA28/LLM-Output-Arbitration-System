# Proposal

## Why

The existing arbitration pipeline has no HTTP entry point. A minimal FastAPI application and health endpoint establish an importable API foundation that can be checked without invoking an LLM.

## What Changes

- Add a FastAPI application that registers a health router.
- Expose `GET /health` with HTTP 200, without provider initialization or LLM calls.
- Add one focused health endpoint test and the dependencies needed to run it.
- Leave arbitration endpoints and the existing pipeline untouched.

## Capabilities

### New Capabilities

- `api-health`: Exposes an HTTP health check independently of arbitration and model providers.

### Modified Capabilities

None.

## Impact

- New API files under `src/api/` and a focused test under `tests/`.
- `pyproject.toml` and `uv.lock` gain the minimal FastAPI and HTTP test dependencies.
- The existing CLI, graph, nodes, prompts, and evaluation behavior remain unchanged.
