# AGENTS.md — LLM Output Arbitration System

## Purpose

This repository contains an **existing, working** LLM response arbitration pipeline built with Python, LangGraph, and Pydantic. The current task is to expose that pipeline through **FastAPI**, using **Spec-Driven Development (SDD)**.

**Do not redesign, rewrite, or expand the arbitration system.** FastAPI is an adapter around the existing application, not a replacement for it.

## Source of truth and precedence

1. The **active, explicitly approved SDD spec** defines what to implement now.
2. This `AGENTS.md` limits scope and protects the existing implementation.
3. Existing source code, schemas, tests, and established behavior define current contracts.
4. The `fastapi-templates` skill provides reference patterns only. It does **not** authorize additional features, folders, or dependencies.

When instructions conflict, preserve existing behavior and the narrower scope. If a change outside the active spec is unavoidable, explain the reason and ask for approval **before** making it. Do not silently broaden the task.

## Mandatory workflow — one spec at a time

1. Read this file, the active spec, and only the relevant existing files before editing.
2. Identify the smallest set of changes needed to meet that spec's acceptance criteria.
3. Implement **only** the active spec. Do not anticipate later specs.
4. Add or update only the tests required for that change.
5. Run targeted tests and existing relevant regression tests. Report exactly what passed, failed, or could not run.
6. Summarize changed files, decisions, and any remaining limitations.
7. Suggest the spec-specific commit message; **do not commit, push, or create branches unless explicitly requested**.
8. Stop after the spec's acceptance criteria are met. Wait for the next spec.

Never claim that unexecuted tests passed. Do not change expected results merely to make tests green.

## Protected existing architecture

Preserve existing implementations and public contracts in:

```text
src/
├── arbitration/
│   ├── graph.py
│   ├── states.py
│   └── schemas/
├── nodes/
├── prompts/
└── ...

tests/
├── evaluation/
├── funcs/
└── ...
```

The existing system includes:

- Three critics: **accuracy, logic, completeness**, executed in parallel.
- Critique collection using LangGraph state reducers.
- Disagreement detection and conditional adjudicator routing.
- Adjudication and structured verdict synthesis.
- An existing CLI/playground and evaluation tests.

**Do not change** nodes, prompts, graph topology, state reducers, enums, scores, verdict semantics, or Pydantic schemas during the API migration unless the active spec explicitly requires it and the change is approved. Do not rename or move existing modules to fit a template.

The API must call the existing `run_agents_graph()` and reuse its existing contracts. Never duplicate the arbitration pipeline in route handlers.

## Target FastAPI structure — minimal, incremental

Create paths only when required by the active spec. This is a **target layout**, not permission to scaffold everything immediately:

```text
src/
├── api/
│   ├── main.py
│   ├── routes/
│   │   ├── health.py
│   │   └── arbitration.py
│   ├── schemas/
│   │   ├── requests.py
│   │   └── responses.py
│   └── services/
│       └── arbitration_service.py
├── arbitration/        # EXISTING — preserve
├── nodes/              # EXISTING — preserve
└── prompts/            # EXISTING — preserve
```

Create only what the current spec needs. `__init__.py` files may be added as needed for packaging. Do not create empty placeholder files, generic abstractions, or folders just to match a template.

## API design boundaries

- Use **FastAPI + Pydantic**; introduce `uvicorn` only as needed to serve the app.
- Keep routes thin: HTTP transport/validation only.
- Put graph orchestration behind a small service function; avoid needless class hierarchies.
- Reuse existing domain schemas where appropriate; define transport schemas only if API boundaries genuinely require them.
- Do not execute blocking `graph.invoke()` directly on an asynchronous event loop. Use a synchronous route or an appropriate execution strategy when the relevant endpoint is implemented.
- Do not initialize provider connections or invoke models just to import the API app or check `/health`.
- Follow existing project imports, configuration conventions, and dependency-management tool (`uv`).
- Never hardcode API keys, tokens, credentials, or secrets.

## Explicitly out of scope unless later approved

- React, Streamlit, or any frontend.
- RAG, document ingestion, embeddings, vector databases, search tools, or MCP.
- PostgreSQL, Redis, ORM, migrations, repositories, or CRUD resources.
- RabbitMQ, Kafka, background workers, distributed jobs, or microservices in Java/Go.
- Authentication, user accounts, roles, billing, rate limiting, or multi-tenancy.
- Docker, Kubernetes, Terraform, cloud deployment, CI/CD, monitoring platforms, or tracing infrastructure.
- New agents, model/provider substitutions, prompt rewrites, adjudication changes, scoring changes, or evaluation redesign.
- Generic `core/`, `utils/`, `base/`, `interfaces/`, `repositories/`, or `config/` frameworks without a concrete requirement.

Do not introduce these components merely because they appear in a FastAPI template or are considered best practices for larger applications.

## Tests and quality rules

- Keep existing test files and behavior intact.
- API unit/integration tests should mock or substitute external LLM calls; no paid requests as a prerequisite to running the test suite.
- Reuse existing pytest conventions; do not switch testing frameworks.
- Cover successful requests and meaningful failures for the feature in the active spec.
- Maintain backward compatibility with the CLI and evaluation runner.
- Prefer readable, minimal code over speculative extensibility.

## Required completion report for each spec

Provide, concisely:

- **Spec implemented** and acceptance criteria met/not met.
- **Files changed** and why.
- **Tests executed** and actual results.
- **Anything intentionally not implemented** because it belongs to another spec.
- **Suggested commit message**.

**Operating rule: implement exactly what was requested, preserve what already works, and stop.**
