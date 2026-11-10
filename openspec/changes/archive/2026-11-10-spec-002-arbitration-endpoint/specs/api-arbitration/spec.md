# Spec Delta

## Purpose

Allows an HTTP client to submit an already-generated answer for evaluation and receive the existing arbitration result as structured data.

## ADDED Requirements

### Requirement: Submit an existing response for evaluation
The API SHALL accept `POST /evaluate` with JSON string fields `original_question` and `generated_output`. Both fields MUST contain non-whitespace text. The API SHALL pass the submitted values to the existing arbitration pipeline without generating a new response.

#### Scenario: Valid evaluation request
- **WHEN** a client posts nonblank `original_question` and `generated_output`
- **THEN** the API evaluates that question and response and returns HTTP 200

#### Scenario: Missing or blank input
- **WHEN** a client omits either field or provides an empty or whitespace-only value
- **THEN** the API returns HTTP 422 without running the arbitration pipeline

### Requirement: Return the graph's structured result
For a completed evaluation, the API SHALL return JSON fields `critiques`, `failed_critics`, `missing_dimensions`, `duplicate_dimensions`, `critiques_complete`, `disagreements`, `requires_adjudication`, `adjudication`, and `verdict`. Critiques, adjudication, and verdict MUST retain their existing field names, values, and verdict semantics.

#### Scenario: Completed evaluation
- **WHEN** the pipeline returns a completed assessment
- **THEN** the response contains its typed critiques, diagnostics, optional adjudication, and verdict without recalculating scores, confidence, issue classification, or status

#### Scenario: Direct synthesis without adjudication
- **WHEN** the pipeline produces a verdict without an adjudication result
- **THEN** the response contains `adjudication: null` and the original verdict

#### Scenario: Inconclusive evaluation
- **WHEN** the pipeline returns an inconclusive verdict after one or more critic failures
- **THEN** the API returns HTTP 200 with that inconclusive verdict and the available critiques and failure diagnostics

### Requirement: Do not expose internal execution errors
If arbitration raises an unexpected exception or produces no valid verdict, the API SHALL return a server error without exposing exception text, credentials, or model payloads.

#### Scenario: Graph execution fails
- **WHEN** arbitration raises an unexpected exception
- **THEN** the API returns HTTP 500 with a generic error response and no exception details
