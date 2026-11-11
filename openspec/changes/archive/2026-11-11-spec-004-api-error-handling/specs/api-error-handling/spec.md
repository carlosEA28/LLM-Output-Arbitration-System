# Spec Delta

## Purpose

Defines safe HTTP behavior when an arbitration API request is invalid, execution times out, or the existing pipeline cannot produce a usable result.

## ADDED Requirements

### Requirement: Reject invalid API input before execution
The arbitration API SHALL return HTTP 422 for missing, non-string, empty, or whitespace-only required text fields and MUST NOT start generation or arbitration for such requests.

#### Scenario: Invalid evaluation request
- **WHEN** either required field of `POST /evaluate` is invalid
- **THEN** the API returns HTTP 422 without invoking arbitration

#### Scenario: Invalid generation request
- **WHEN** the required question of `POST /generate-and-evaluate` is invalid
- **THEN** the API returns HTTP 422 without invoking generation or arbitration

### Requirement: Distinguish propagated timeouts from other execution failures
The arbitration API SHALL return HTTP 504 with a fixed, safe response when generation or arbitration propagates a timeout. It SHALL return HTTP 500 with a fixed, safe response for other execution failures or an unusable result. Failure responses MUST omit exception text, stack traces, credentials, private prompts, and provider payloads.

#### Scenario: Evaluation times out
- **WHEN** `POST /evaluate` arbitration propagates a timeout
- **THEN** the API returns HTTP 504 with no internal details

#### Scenario: Generation or subsequent arbitration times out
- **WHEN** `POST /generate-and-evaluate` generation or arbitration propagates a timeout
- **THEN** the API returns HTTP 504 with no internal details

#### Scenario: Other execution failure or unusable result
- **WHEN** an endpoint encounters a non-timeout execution failure or no valid verdict
- **THEN** the API returns HTTP 500 with no internal details

### Requirement: Preserve usable inconclusive outcomes
The API SHALL treat a valid graph verdict with `status: inconclusive` as a result and MUST preserve the existing verdict and available failure diagnostics.

#### Scenario: Critic timeout absorbed by graph
- **WHEN** a critic failure is reflected in a valid inconclusive graph verdict instead of propagating as an exception
- **THEN** the API returns HTTP 200 with that verdict and its available diagnostics
