# Design

## Context

See `proposal.md` for motivation and `specs/api-arbitration/spec.md` for the HTTP contract. `src.api.main` currently registers only `GET /health`. `run_agents_graph()` compiles the existing graph, and the CLI invokes it with `original_question`, `generated_output`, empty `critiques`, and empty `failed_critics`. The graph returns domain Pydantic objects for critiques, adjudication, and verdict. `graph.invoke()` is synchronous and can perform model calls.

## Goals / Non-Goals

**Goals:**
- Keep HTTP parsing, validation, and error mapping in the route; keep graph invocation in one small service function.
- Serialize the graph's evaluation fields through transport schemas that reuse domain Pydantic models.
- Make endpoint tests deterministic without paid model calls.

**Non-Goals:**
- Change graph execution, verdict synthesis, provider behavior, or the CLI.
- Generate the answer being evaluated, add background jobs, or define a new scoring format.

## Decisions

- Use request fields `original_question` and `generated_output`, matching the graph state and CLI call. A transport Pydantic model rejects missing, non-string, empty, and whitespace-only values before invocation. Introducing HTTP-only synonyms would add translation without a requirement.
- Add a synchronous `POST /evaluate` route in `src/api/routes/arbitration.py` and register it in `src/api/main.py`. FastAPI runs a synchronous route off the event loop while the service compiles and invokes the graph. An async route calling `graph.invoke()` directly could block the event loop.
- Add one service function in `src/api/services/arbitration_service.py` that calls `run_agents_graph()` and invokes the resulting graph with the two inputs and the reducer list initializers. Return graph output for serialization, without computing a new verdict. Calling graph nodes from the route or reimplementing synthesis would duplicate established behavior.
- Use an API response model in `src/api/schemas/responses.py` for the nine fields named in the spec, reusing `CritiqueSchema`, `AdjudicationSchema`, and `VerdictSchema`. Map an absent `adjudication` to JSON `null` for the direct synthesis path; require a valid `verdict`. If the graph raises or returns no valid verdict, return a generic HTTP 500; never include raw exception text. Returning the full internal state would expose inputs and incidental fields without a stable API contract.
- Test via `TestClient` and substitute graph execution at the service boundary. Check the exact invocation payload, successful serialization, inconclusive status and partial diagnostics, validation rejection without invocation, and sanitized execution failure. Existing health and graph routing tests provide focused regression checks.

## Risks / Trade-offs

- Model calls may take longer than a health request → Keep the route synchronous so they do not block the event loop; timeouts and async jobs are outside this spec.
- Graph results may contain missing or malformed required fields → Return a generic server error instead of inventing defaults or a replacement verdict.
- An unexpected graph exception could contain sensitive provider details → Respond with a fixed, generic error body and no exception text.
