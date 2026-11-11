# Spec Delta

## MODIFIED Requirements

### Requirement: Return generated text and the existing evaluation result
On success, the API SHALL return a unique `id`, `generated_output`, and the evaluation fields `critiques`, `failed_critics`, `missing_dimensions`, `duplicate_dimensions`, `critiques_complete`, `disagreements`, `requires_adjudication`, `adjudication`, and `verdict`. The `id` MUST identify the persisted execution retrievable through `GET /v1/arbitrations/{id}`. Evaluation values and verdict semantics MUST be preserved.

#### Scenario: Completed evaluation
- **WHEN** generation produces an answer and arbitration returns a valid result
- **THEN** `generated_output` contains the answer that was evaluated, `id` identifies its persisted record, and the other fields contain the corresponding structured arbitration result

#### Scenario: Direct synthesis or partial evaluation
- **WHEN** arbitration returns no adjudication or an inconclusive verdict with critic failure diagnostics
- **THEN** the API returns HTTP 200 with `adjudication: null` where absent, preserves the verdict and diagnostics, and supplies the persisted execution ID

## ADDED Requirements

### Requirement: Make failed execution IDs available
For a valid `POST /generate-and-evaluate` request that ends in HTTP 500 or 504 after a history record is created, the API SHALL include its ID in the `X-Arbitration-ID` response header while retaining the existing generic error body. The same header SHALL appear on successful responses.

#### Scenario: Execution fails after record creation
- **WHEN** generation or evaluation ends in HTTP 500 or 504
- **THEN** the response keeps its existing generic error body and includes a retrievable `X-Arbitration-ID`

#### Scenario: Successful execution
- **WHEN** generation and evaluation complete successfully
- **THEN** `X-Arbitration-ID` matches the `id` in the response body
