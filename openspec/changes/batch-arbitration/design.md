# Design

## Context

See `proposal.md` for motivation and `specs/batch-arbitration/spec.md` for the HTTP contract. `POST /evaluate` already validates each question and response with `EvaluationRequest`, invokes the existing graph through `evaluate_response()`, and serializes the result with `EvaluationResponse`. The route is synchronous, so FastAPI runs blocking graph invocation outside the event loop. Request validation errors use a sanitized HTTP 422 response. Only `/generate-and-evaluate` writes arbitration history.

## Goals / Non-Goals

**Goals:** Reuse the existing evaluation service and response model, preserve input order, isolate execution failures per item, and maintain safe error messages.

**Non-Goals:** Generate responses, persist batch items, add parallel workers or retries, or change graph and verdict behavior.

## Decisions

1. Use a transport request model with `items: list[EvaluationRequest]` and a minimum length of one. Validation of the whole request precedes execution, so an invalid item rejects the batch with the existing sanitized 422 response. Allowing per-item invalid input would require a separate item validation contract and complicate the result schema.
2. Add a synchronous batch route that loops over validated items in order and calls `evaluate_response()` once per item. Sequential execution avoids new concurrency limits and provider load behavior while keeping the route off the event loop. The route does not call `run_agents_graph()` directly.
3. Reuse `EvaluationResponse` for a completed result. Wrap each outcome with a zero-based index, status, nullable evaluation, and nullable fixed error message. A valid inconclusive verdict is completed, matching `/evaluate`.
4. Catch timeouts and other failures inside each iteration, including response-model validation failures. Return generic `Evaluation timed out` or `Evaluation failed` messages without exception content. Return HTTP 200 for any valid batch, including all-failure batches, because the response represents independent outcomes.
5. Do not call the history module. The existing persistence boundary is limited to generation and evaluation requests; batch evaluation handles already-generated responses like `/evaluate`.

## Risks / Trade-offs

- [A large batch can take a long time because evaluations run sequentially] → Keep execution simple and document the behavior; batch size limits and parallel execution require separate product decisions.
- [A provider timeout can delay later items] → Continue processing subsequent items once that call returns or raises; the endpoint cannot override a provider call that never terminates.
- [HTTP 200 does not imply every item succeeded] → Require clients to inspect each result's `status`.
