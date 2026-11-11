# api-generation Specification

## Purpose

Allows an HTTP client to submit one question and receive the project's generated answer together with its existing arbitration assessment.

## Requirements

### Requirement: Accept a question for generation and evaluation
The API SHALL accept `POST /generate-and-evaluate` with a JSON string field `original_question` containing non-whitespace text. It SHALL generate one answer using the project's existing generator configuration, then evaluate that answer through the existing arbitration pipeline.

#### Scenario: Valid question
- **WHEN** a client submits a nonblank `original_question`
- **THEN** the API generates an answer, evaluates that answer against the submitted question, and returns HTTP 200

#### Scenario: Invalid question
- **WHEN** `original_question` is missing, not a string, empty, or whitespace-only
- **THEN** the API returns HTTP 422 without invoking generation or arbitration

### Requirement: Return generated text and the existing evaluation result
On success, the API SHALL return a unique `id`, `generated_output`, and the evaluation fields `critiques`, `failed_critics`, `missing_dimensions`, `duplicate_dimensions`, `critiques_complete`, `disagreements`, `requires_adjudication`, `adjudication`, and `verdict`. The `id` MUST identify the persisted execution retrievable through `GET /v1/arbitrations/{id}`. Evaluation values and verdict semantics MUST be preserved.

#### Scenario: Completed evaluation
- **WHEN** generation produces an answer and arbitration returns a valid result
- **THEN** `generated_output` contains the answer that was evaluated, `id` identifies its persisted record, and the other fields contain the corresponding structured arbitration result

#### Scenario: Direct synthesis or partial evaluation
- **WHEN** arbitration returns no adjudication or an inconclusive verdict with critic failure diagnostics
- **THEN** the API returns HTTP 200 with `adjudication: null` where absent, preserves the verdict and diagnostics, and supplies the persisted execution ID

### Requirement: Keep generation and evaluation failures private
The API SHALL return a generic server error if generation fails, yields no nonblank answer, or arbitration fails or returns no valid verdict. Error responses MUST NOT expose provider exception text, credentials, or model payloads.

#### Scenario: Generation failure
- **WHEN** the generator raises an exception or yields a blank answer
- **THEN** the API returns HTTP 500 without invoking arbitration or exposing internal details

#### Scenario: Arbitration failure
- **WHEN** arbitration raises an exception or returns no valid verdict after an answer is generated
- **THEN** the API returns HTTP 500 without exposing internal details

### Requirement: Make failed execution IDs available
For a valid `POST /generate-and-evaluate` request that ends in HTTP 500 or 504 after a history record is created, the API SHALL include its ID in the `X-Arbitration-ID` response header while retaining the existing generic error body. The same header SHALL appear on successful responses.

#### Scenario: Execution fails after record creation
- **WHEN** generation or evaluation ends in HTTP 500 or 504
- **THEN** the response keeps its existing generic error body and includes a retrievable `X-Arbitration-ID`

#### Scenario: Successful execution
- **WHEN** generation and evaluation complete successfully
- **THEN** `X-Arbitration-ID` matches the `id` in the response body
