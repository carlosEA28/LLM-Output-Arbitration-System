# Tasks

## 1. API contract coverage

- [ ] 1.1 Compare `tests/test_evaluate_api.py`, `tests/test_generate_and_evaluate_api.py`, and `tests/test_arbitration_service.py` with the SPEC-002 through SPEC-004 contracts; verify the comparison identifies existing coverage for request validation, success, graph invocation, inconclusive results, timeout handling, and safe failures.
- [ ] 1.2 Add only uncovered deterministic API or service cases in the nearby pytest files, with mocked generation and graph calls; verify `uv run pytest tests/test_evaluate_api.py tests/test_generate_and_evaluate_api.py tests/test_arbitration_service.py` passes and no test makes a paid provider request.

## 2. Regression checks

- [ ] 2.1 Run the relevant graph routing, adjudication, CLI generation, health, and evaluation-runner pytest files with `uv run pytest`; report the exact commands and pass, fail, or unavailable results, including any regression that remains unresolved.
