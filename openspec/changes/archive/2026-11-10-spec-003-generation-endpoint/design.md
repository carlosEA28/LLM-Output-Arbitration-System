# Design

## Context

See `proposal.md` for motivation and `specs/api-generation/spec.md` for the HTTP contract. The CLI currently creates `ChatOpenAI(model="gpt-5-mini")`, invokes it with the question, converts `response.content` to text, and then invokes `run_agents_graph()` with the question and generated text. `POST /evaluate` already wraps that graph call in `evaluate_response()` and serializes nine evaluation fields. Both model and graph calls are synchronous.

## Goals / Non-Goals

**Goals:**
- Share the CLI's generator configuration and call with the API while preserving CLI behavior.
- Reuse the existing evaluation service and response model for arbitration data.
- Keep provider initialization and model calls out of app import and `/health`.

**Non-Goals:**
- Move generation into the graph, alter critics or verdict synthesis, or change provider/model selection.
- Add streaming, background jobs, retries, or new infrastructure.

## Decisions

- Extract the CLI's generator construction, invocation, and text conversion into a small function in the existing CLI module; call it from both the CLI and the API service. This keeps one configured generation path. Duplicating the `ChatOpenAI` call in the API would allow the two paths to drift; adding a new graph node would change protected topology.
- Add a question-only request model using the same strict, nonblank validation as `EvaluationRequest`. Add a response model that extends the existing `EvaluationResponse` with `generated_output`. This retains the existing field types and keeps `/evaluate` unchanged. Returning the entire graph state would expose internal fields without a stable contract.
- Add a synchronous route in the existing arbitration router. A small service function generates once, verifies nonblank text, then calls `evaluate_response(original_question, generated_output)`. The route handles HTTP validation and converts generation, graph, or response validation failures to a fixed HTTP 500 body. Synchronous execution keeps the blocking calls off the event loop.
- Test the endpoint with controlled generator and evaluation service results, and test the shared generator function with a substituted `ChatOpenAI` model. Verify call order and exact generated text passed to evaluation, invalid input short circuiting, partial results, and sanitized failures. Run existing `/evaluate`, health, service, and CLI relevant regression checks.

## Risks / Trade-offs

- A provider response with blank content cannot be evaluated → fail before calling the graph and return a generic server error.
- A slow model call holds one worker thread for the request → retain synchronous execution; request timeouts and queued jobs are outside this change.
- Sharing generation through the CLI module couples the API to that module's imports → keep the helper small and free of import-time model initialization.
