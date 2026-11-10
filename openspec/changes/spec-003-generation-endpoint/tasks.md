# Tasks

## 1. Shared generation path

- [x] 1.1 Extract the existing `ChatOpenAI(model="gpt-5-mini")` generation call into a small function used by the CLI; verify a controlled-model test observes the same model choice, question, and text conversion.
- [x] 1.2 Add a service function that generates once, rejects blank generated text, and passes the exact question and answer to `evaluate_response()`; verify controlled service tests cover call order, successful data, and no graph call for blank output.

## 2. Generation endpoint

- [x] 2.1 Add a strict, nonblank question request model and a response model containing `generated_output` plus the existing evaluation fields; verify endpoint tests reject missing, non-string, and blank questions with HTTP 422 before either service runs.
- [ ] 2.2 Add synchronous `POST /generate-and-evaluate` to the existing arbitration router; verify controlled endpoint tests return the generated answer and unchanged structured evaluation fields, including null adjudication and partial inconclusive results.
- [ ] 2.3 Map generation, arbitration, blank-output, and malformed-verdict failures to a generic HTTP 500 response; verify endpoint tests expose no exception text or model payloads and do not evaluate after generation failure.

## 3. Integration checks

- [ ] 3.1 Run the new focused tests plus existing `/evaluate`, health, and arbitration service regression tests with `uv run pytest`; record actual results and verify the CLI and existing endpoint contracts remain intact.
