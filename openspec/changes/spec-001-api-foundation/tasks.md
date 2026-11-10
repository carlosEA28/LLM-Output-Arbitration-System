# Tasks

## 1. API dependencies

- [x] 1.1 Add `fastapi` and `httpx` to `pyproject.toml`, update `uv.lock` with `uv`, and verify the lockfile resolves successfully.

## 2. Health API

- [x] 2.1 Create `src/api/main.py` and `src/api/routes/health.py` with minimal package initializers as needed; verify `src.api.main.app` imports and registers `GET /health` without importing arbitration or provider modules.
- [x] 2.2 Add one focused pytest test for `GET /health` that verifies HTTP 200 without model configuration; verify it passes with `uv run pytest tests/test_health.py`.

## 3. Integration check

- [x] 3.1 Run the health test and the existing graph routing regression test, and record the actual results without changing the arbitration pipeline.
