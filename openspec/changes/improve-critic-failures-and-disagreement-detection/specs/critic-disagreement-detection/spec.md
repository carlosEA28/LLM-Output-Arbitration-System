# Spec Delta

## Purpose

This capability distinguishes substantive contradictions between critics' explicit findings from ordinary differences between evaluation dimensions.

## ADDED Requirements

### Requirement: Exclude unsupported disagreements
The system SHALL NOT report a disagreement solely because critics assign different scores, evaluate different dimensions, or one critic reports an issue that another does not mention.

#### Scenario: Different dimension scores
- **WHEN** accuracy and completeness assign different scores without incompatible issue claims
- **THEN** no disagreement is reported and adjudication is not required

#### Scenario: Issue and silence
- **WHEN** one critic reports an issue and another reports no issue
- **THEN** that difference alone produces no disagreement or adjudication request

#### Scenario: Compatible issues
- **WHEN** critics report issues about different, compatible aspects of the answer
- **THEN** no disagreement is reported and adjudication is not required

### Requirement: Report supported contradictions
The system SHALL report a disagreement only when two available critics make explicit incompatible claims about the same aspect of the answer, and SHALL require adjudication when at least one such disagreement is found.

#### Scenario: Conflicting claims
- **WHEN** two critics explicitly assess the same answer claim in incompatible ways
- **THEN** the disagreement identifies the two implicated issues and adjudication is required

#### Scenario: Invalid conflict reference
- **WHEN** a proposed conflict references a missing issue, two issues from the same critic, or a conflict already reported
- **THEN** that proposed conflict is excluded from the disagreements

### Requirement: Handle incomplete evidence honestly
The system SHALL NOT infer agreement or disagreement from a missing or failed critic and SHALL preserve available critiques, including critical issues, whether or not adjudication is required.

#### Scenario: One available critique
- **WHEN** only one critic provides an evaluation
- **THEN** no cross-critic disagreement is reported and the available critique remains in the result

#### Scenario: No available critiques
- **WHEN** no critic provides an evaluation
- **THEN** no disagreement is reported, adjudication is not required on disagreement grounds, and the evaluation set remains incomplete

#### Scenario: Critical issue without conflict
- **WHEN** an available critique contains a critical issue and no other critic makes an incompatible claim
- **THEN** the critical issue remains available and adjudication is not required on disagreement grounds
