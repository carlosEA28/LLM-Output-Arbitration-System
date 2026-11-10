# Proposal

## Why

The API already has endpoint and service tests, but the requested regression pass should verify the full API contract and existing arbitration behavior together after SPEC-004. This change adds only missing coverage and records actual results without changing product behavior.

## What Changes

- Audit existing API tests for request validation, successful responses, graph invocation, and failure paths; add only missing cases.
- Run relevant arbitration, adjudication, CLI, and evaluation regressions with external model calls mocked or substituted.
- Report any failures or tests that cannot run; do not change expected behavior merely to obtain a passing suite.

## Capabilities

### New Capabilities

None. This is a test-only change with `skip_specs: true`.

### Modified Capabilities

None. Existing API and arbitration requirements remain the acceptance criteria.

## Impact

Only relevant test files and the test report. No API, graph, CLI, evaluation-runner, dependency, or infrastructure changes are planned. Apply this change after SPEC-004 so its timeout behavior is included in the regression pass.
