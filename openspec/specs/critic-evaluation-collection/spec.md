# critic-evaluation-collection Specification

## Purpose

This capability preserves the outcomes of parallel critic evaluations and tells downstream processing whether the expected evidence is complete.

## Requirements

### Requirement: Preserve successful evaluations alongside failures
The system SHALL retain each successful critic evaluation and record each critic that fails, without discarding successful evaluations because another critic failed.

#### Scenario: All critics succeed
- **WHEN** accuracy, logic, and completeness critics each return an evaluation
- **THEN** the result contains one evaluation for each of the three dimensions and no failed critics

#### Scenario: One critic fails
- **WHEN** one critic fails and the other two return evaluations
- **THEN** the result contains both successful evaluations and identifies the failed critic

#### Scenario: All critics fail
- **WHEN** all three critics fail
- **THEN** the result contains no evaluations and identifies all three failed critics

### Requirement: Report evaluation completeness
The system SHALL identify absent and duplicate dimensions and SHALL mark the evaluation set complete only when each expected dimension appears exactly once and no critic failure is recorded.

#### Scenario: Complete evaluations
- **WHEN** each expected dimension appears once and no critic failed
- **THEN** no dimension is missing or duplicated and the evaluation set is complete

#### Scenario: Partial evaluations
- **WHEN** a critic fails without providing its evaluation
- **THEN** its dimension is reported missing and the evaluation set is incomplete

#### Scenario: No evaluations
- **WHEN** all three critics fail
- **THEN** all three dimensions are reported missing, the evaluation set is incomplete, and no successful verdict is produced

#### Scenario: Duplicate evaluation
- **WHEN** any dimension appears more than once
- **THEN** that dimension is reported duplicated and the evaluation set is incomplete

### Requirement: Preserve transient retry behavior
Each critic SHALL retain the existing retry behavior for transient model failures and SHALL record a failure when its allowed attempts are exhausted.

#### Scenario: Transient failure followed by success
- **WHEN** a critic encounters a transient failure and succeeds on its allowed retry
- **THEN** its evaluation is retained and that critic is not recorded as failed

#### Scenario: Exhausted retries
- **WHEN** a critic exhausts its allowed attempts on transient failures
- **THEN** that critic is recorded as failed and its evaluation is absent
