# issue-adjudication Specification

## Purpose

This capability resolves explicit conflicts between available critic findings while preserving the evidence and uncertainty needed for a defensible final verdict.

## Requirements

### Requirement: Resolve reported conflicts
When adjudication is required, the system SHALL assess the original question, generated response, available critiques, and reported disagreements and return structured decisions about issues.

#### Scenario: Genuine contradiction
- **WHEN** two critics make incompatible claims about the same aspect of the response
- **THEN** adjudication identifies which implicated issues are confirmed or dismissed and explains each dismissal

#### Scenario: Independent dimensions
- **WHEN** critics describe compatible findings from different evaluation dimensions
- **THEN** adjudication does not dismiss either finding solely because their scores differ

### Requirement: Ground issue decisions
The system SHALL base confirmed and dismissed issues on supplied critic issues, SHALL NOT invent evidence or citations, and SHALL acknowledge claims that cannot be independently verified.

#### Scenario: Unverifiable factual claim
- **WHEN** the available input does not establish whether a factual claim is true
- **THEN** adjudication records the uncertainty rather than asserting an unverified fact as established

#### Scenario: Unsupported issue in model output
- **WHEN** a proposed decision refers to an issue absent from the supplied critiques
- **THEN** that proposed decision is not accepted as a grounded adjudication result

### Requirement: Preserve undecided findings
The system SHALL preserve critic issues that adjudication has not explicitly and validly dismissed.

#### Scenario: Unrelated factual issue
- **WHEN** adjudication resolves one conflict and a separate factual issue is present
- **THEN** the separate factual issue remains available for the final verdict
