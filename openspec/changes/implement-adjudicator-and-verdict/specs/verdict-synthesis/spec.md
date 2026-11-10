# Spec Delta

## Purpose

This capability turns the available critic assessments and any adjudication decisions into a structured final verdict that states the limits of its evidence.

## ADDED Requirements

### Requirement: Produce a bounded verdict
The system SHALL produce a verdict containing an integer overall score from 1 to 10, a confidence value from 0 to 1, confirmed issues, dismissed issues with reasons, and a concise summary.

#### Scenario: Complete evaluations
- **WHEN** all three critic dimensions return evaluations
- **THEN** the final graph state contains a valid verdict with bounded score and confidence

### Requirement: Complete both graph routes
The system SHALL produce a final verdict after adjudication and when adjudication is unnecessary, without adding a synthesis model call.

#### Scenario: Disagreement route
- **WHEN** a reported disagreement requires adjudication
- **THEN** the graph applies grounded adjudication decisions before producing the verdict

#### Scenario: Direct route with factual issue
- **WHEN** no adjudication is required and an available accuracy critique reports a factual issue
- **THEN** the verdict retains that issue among confirmed findings

### Requirement: Reflect incomplete evidence
The verdict SHALL reduce its confidence when critic dimensions are missing, duplicated, or recorded as failed, and SHALL describe confidence as an assessment heuristic rather than a calibrated probability.

#### Scenario: Partial critic failure
- **WHEN** one critic fails and two provide evaluations
- **THEN** the verdict retains their legitimate issues and has lower confidence than a complete evaluation

### Requirement: Mark total critic failure inconclusive
When no critic returns an evaluation, the system SHALL return an explicitly inconclusive verdict with zero confidence and no confirmed issues; its required score field SHALL use 1 as a sentinel, not as an assessment of answer quality.

#### Scenario: All critics fail
- **WHEN** all critic evaluations fail or no critiques are available
- **THEN** the verdict is marked inconclusive, has confidence 0, and explains that no assessment was possible
