# Design

## Context

The repository currently has a CLI and LangGraph application under `src/arbitration/`, but no `src/api/` package or declared FastAPI dependency. See `proposal.md` for the motivation and `specs/api-health/spec.md` for the HTTP contract. Existing imports use the `src.*` package path, and dependencies are managed with `uv`.

## Goals / Non-Goals

**Goals:**
- Make an importable FastAPI `app` available from `src.api.main`.
- Register a small health router at the application entry point.
- Keep app import and health requests independent of graph and provider modules.

**Non-Goals:**
- Add arbitration routes, orchestration services, response schemas, or startup model checks.
- Add server deployment configuration, middleware, or template framework components.

## Decisions

- Add only `src/api/main.py`, `src/api/routes/health.py`, and package initializers if import resolution needs them. `main.py` creates the FastAPI instance and includes the health router; `health.py` defines `GET /health`. This follows the repository's target layout while keeping route registration explicit. A single-file app would be shorter, but would omit the requested router registration boundary.
- Keep the health module free of `src.arbitration` and provider imports. The endpoint returns a small static response with HTTP 200; the response body is an implementation detail because the spec only fixes the status. A graph-backed check would make health depend on model configuration and could trigger paid calls.
- Add `fastapi` for the app and `httpx` for FastAPI's `TestClient` to `pyproject.toml`, updating `uv.lock` with `uv`. Use one focused pytest test that sends `GET /health` and asserts HTTP 200. Existing tests already use pytest; a live server or provider-backed test is unnecessary.

## Risks / Trade-offs

- A static health result proves the API process responds, but does not establish provider availability → Keep that limit explicit; provider health is outside this spec.
- An accidental provider import in API modules could add startup side effects → Keep imports restricted to FastAPI and the health router, and verify the health test runs without provider configuration.
