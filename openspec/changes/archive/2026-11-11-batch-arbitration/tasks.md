# Tasks

## 1. Batch transport contract

- [x] 1.1 Add a nonempty batch request model reusing `EvaluationRequest` and result models reusing `EvaluationResponse` in `src/api/schemas/`; verify schema validation accepts independent valid pairs and rejects empty or invalid items.
- [x] 1.2 Add focused API tests for request-level HTTP 422 and no evaluation calls on invalid batch input; verify with `uv run pytest tests/test_batch_arbitration_api.py`.

## 2. Independent evaluation outcomes

- [x] 2.1 Add synchronous `POST /v1/arbitrate/batch` in `src/api/routes/arbitration.py` that calls `evaluate_response()` per item and returns ordered, indexed outcomes; verify multiple successful items retain their evaluation fields and call order in `uv run pytest tests/test_batch_arbitration_api.py`.
- [x] 2.2 Handle propagated timeouts, other exceptions, and unusable results per item with fixed safe errors while continuing the batch; verify mixed results, all-failure HTTP 200, and inconclusive verdict behavior in `uv run pytest tests/test_batch_arbitration_api.py`.
- [x] 2.3 Verify batch processing creates no history records and existing `/evaluate` and `/generate-and-evaluate` behavior remains intact with focused assertions and `uv run pytest tests/test_batch_arbitration_api.py tests/test_evaluate_api.py tests/test_generate_and_evaluate_api.py tests/test_arbitration_history_api.py`.
