# Spec Delta

## MODIFIED Requirements

### Requirement: Keep generation and evaluation failures private
The API SHALL return a generic HTTP 500 response if generation fails for a reason other than a propagated timeout, yields no nonblank answer, or arbitration fails or returns no valid verdict for a reason other than a propagated timeout. A propagated generation or arbitration timeout SHALL return a generic HTTP 504 response. Error responses MUST NOT expose provider exception text, credentials, private prompts, or model payloads.

#### Scenario: Generation failure
- **WHEN** the generator raises a non-timeout exception or yields a blank answer
- **THEN** the API returns HTTP 500 without invoking arbitration or exposing internal details

#### Scenario: Arbitration failure
- **WHEN** arbitration raises a non-timeout exception or returns no valid verdict after an answer is generated
- **THEN** the API returns HTTP 500 without exposing internal details

#### Scenario: Generation timeout
- **WHEN** generation propagates a timeout
- **THEN** the API returns HTTP 504 without invoking arbitration or exposing internal details

#### Scenario: Arbitration timeout
- **WHEN** arbitration propagates a timeout after an answer is generated
- **THEN** the API returns HTTP 504 without exposing internal details
