# Tasks

## 1. Timeout and safe failure responses

- [x] 1.1 Add narrow propagated-timeout handling to both existing API routes while retaining fixed HTTP 500 fallbacks; verify focused endpoint tests return HTTP 504 for recognized timeouts and omit exception text, prompt content, and credentials.
- [x] 1.2 Verify invalid input still returns HTTP 422 before any service call, malformed results still return safe HTTP 500, and valid inconclusive results still return HTTP 200 with unchanged diagnostics in focused API tests.

## 2. Integration checks

- [x] 2.1 Run the focused API tests and existing relevant graph, CLI, and evaluation regression tests with `uv run pytest`; report actual pass, fail, or unavailable results without changing protected arbitration behavior.
