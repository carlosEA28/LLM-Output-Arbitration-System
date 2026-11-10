# Design

## Context

See `proposal.md`. Existing tests cover `/evaluate`, `/generate-and-evaluate`, the shared service, health, graph routing, adjudication flow, CLI generation, and evaluation reporting. SPEC-004 defines the timeout behavior this regression pass will verify. The suite already uses pytest and controlled model or graph substitutes.

## Goals / Non-Goals

**Goals:**
- Check the API boundary and existing arbitration contracts with deterministic tests.
- Run relevant regression suites and report actual results.

**Non-Goals:**
- Add runtime features, alter domain semantics, or introduce live provider calls.

## Decisions

- Reuse nearby pytest fixtures and monkeypatch patterns. Add cases only for uncovered contract edges after comparing existing tests against SPEC-004 and the established endpoint specs. A new generic test harness would add maintenance cost without improving this small suite.
- Keep endpoint tests at the HTTP boundary and a separate service assertion for `run_agents_graph()` input. HTTP tests prove status and safe response bodies; service tests prove the graph is invoked with the existing CLI state. Combining both in every test would duplicate assertions.
- Run API tests and targeted graph, adjudication, CLI, and evaluation tests with `uv run pytest`. Record exact commands and outcomes. Provider calls must remain mocked or substituted; a live evaluation run is outside this test pass.

## Risks / Trade-offs

- Some existing tests may already satisfy the requested coverage → document them and add no duplicate test.
- A regression failure may reveal a product defect beyond SPEC-005 → report it without silently changing protected behavior.
