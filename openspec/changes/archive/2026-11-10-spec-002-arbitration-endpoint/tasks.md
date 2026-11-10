# Tasks

## 1. Graph service

- [x] 1.1 Add `src/api/services/arbitration_service.py` with a small function that compiles and invokes `run_agents_graph()` using the existing input state; verify with a mocked graph test that the exact input keys and values reach `invoke()` once.

## 2. Evaluation API

- [x] 2.1 Add minimal request and response schemas under `src/api/schemas/`, reusing domain critique, adjudication, and verdict models; verify endpoint tests reject missing or blank input with HTTP 422 and no graph invocation.
- [x] 2.2 Add a synchronous `POST /evaluate` route and register it in `src/api/main.py`; verify a controlled graph result returns HTTP 200 with the nine specified response fields and unchanged verdict values.
- [x] 2.3 Map absent adjudication to `null` and preserve partial results with an inconclusive verdict; verify both paths with controlled endpoint tests and no model calls.
- [x] 2.4 Return a generic HTTP 500 when graph execution fails or no valid verdict is available; verify endpoint tests do not expose exception text or model payloads.

## 3. Integration checks

- [x] 3.1 Run the endpoint tests plus existing `tests/test_health.py` and `tests/test_graph_routing.py`; record actual results and verify the graph and CLI source files remain unchanged.
