# batch-arbitration Specification

## Purpose

Allows clients to evaluate several independent, already-generated responses in one request while retaining each item's outcome when other evaluations fail.

## Requirements

### Requirement: Accept a batch of evaluation pairs
The API SHALL accept `POST /v1/arbitrate/batch` with a JSON object containing a nonempty `items` array. Each item MUST contain nonblank string fields `original_question` and `generated_output`. Invalid input SHALL return HTTP 422 before any evaluation starts.

#### Scenario: Valid batch input
- **WHEN** a client submits two or more valid items with independent questions and responses
- **THEN** the API evaluates each submitted pair without generating new responses

#### Scenario: Invalid item or empty batch
- **WHEN** `items` is absent or empty, or any item has a missing, non-string, empty, or whitespace-only required field
- **THEN** the API returns HTTP 422 and evaluates no items

### Requirement: Report each item independently in input order
For valid input, the API SHALL return HTTP 200 with a `results` array containing exactly one entry per input item in the same order. Each entry SHALL include its zero-based `index` and a `status` of `completed`, `failed`, or `timed_out`. A completed entry SHALL include an `evaluation` with the existing structured evaluation fields and `error: null`.

#### Scenario: All evaluations complete
- **WHEN** every item produces a valid evaluation
- **THEN** every result has `status: completed`, its corresponding index, and its original verdict and diagnostics

#### Scenario: Inconclusive graph verdict
- **WHEN** an item produces a valid inconclusive verdict with critic failure diagnostics
- **THEN** that item is `completed` and retains the inconclusive verdict and diagnostics

### Requirement: Preserve partial execution failures safely
An item whose evaluation times out SHALL have `status: timed_out`; another execution failure or unusable result SHALL have `status: failed`. Failed entries SHALL contain `evaluation: null` and a fixed, safe `error` message. The API MUST continue with remaining items and MUST NOT expose exception text, credentials, prompts, or provider payloads.

#### Scenario: Mixed outcomes
- **WHEN** one item succeeds, one times out, and one fails
- **THEN** the response contains all three ordered results, with independent statuses and no internal error details

#### Scenario: Every evaluation fails
- **WHEN** all items fail after valid input is accepted
- **THEN** the API returns HTTP 200 with one safe failure result per item

### Requirement: Preserve existing endpoint and history contracts
Batch evaluation SHALL NOT create arbitration history records and SHALL NOT alter the behavior or response contract of `POST /evaluate` or `POST /generate-and-evaluate`.

#### Scenario: Batch request does not persist
- **WHEN** a valid batch is evaluated
- **THEN** no arbitration history record is created for its items
