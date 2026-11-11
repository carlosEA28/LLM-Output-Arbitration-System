# Design

## Context

See `proposal.md` and the delta specs. Both API routes are synchronous and already catch all exceptions, returning fixed HTTP 500 details. Request schemas already reject non-string and blank fields. The graph can return a valid `inconclusive` verdict after critic failures; those failures are data, not propagated exceptions.

## Goals / Non-Goals

**Goals:**
- Classify propagated timeout exceptions at the HTTP boundary without exposing their messages.
- Preserve existing request and verdict contracts, including partial results.

**Non-Goals:**
- Impose a new wall-clock deadline or cancel a running graph or provider call.
- Change retry behavior, provider configuration, graph nodes, CLI behavior, or verdict synthesis.

## Decisions

- Keep the existing synchronous service and route structure. Add a narrow timeout exception branch before the generic exception branch in each route. The alternative of a global exception handler would affect unrelated endpoints and hide the endpoint-specific fixed messages.
- Match concrete timeout exception types used at this boundary, starting with built-in `TimeoutError` and the already-installed `httpx.TimeoutException`; include a provider timeout type only if it is directly available through existing dependencies. Do not classify an error by searching exception text, since text may contain sensitive data or misidentify failures. Other exceptions retain HTTP 500.
- Use fixed response details for HTTP 504 and 500. Never include `str(exception)`, traceback text, request data, or graph state in an error body. Keep response-model validation inside the protected route block so malformed results also become fixed HTTP 500 responses.
- Leave request models and valid-result serialization unchanged. A focused test showed that FastAPI's default HTTP 422 body echoes rejected input, so add a fixed request-validation response body at app setup while retaining HTTP 422 and early rejection. A valid `inconclusive` verdict continues through normal response serialization and returns HTTP 200.

## Risks / Trade-offs

- A provider may wrap a timeout in an unrelated exception class → it will receive the safe HTTP 500 fallback; focused tests should cover timeout classes the implementation explicitly recognizes.
- HTTP 504 only classifies a timeout that propagates to the API → it does not stop a slow synchronous call. A request deadline would need separate cancellation and provider configuration work.
