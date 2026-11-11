# Evaluation runner — LLM Output Arbitration System

Copy the `tests/` files into the root of your existing repository, keeping the existing `src/` directory unchanged. If `tests/__init__.py` or `tests/evaluation/__init__.py` already exists, keep it.

From the project root:

```bash
uv run python -m pytest tests/evaluation/test_evaluate.py -v
uv run python -m tests.evaluation.evaluate --limit 3
uv run python -m tests.evaluation.evaluate
```

The first command runs **offline unit tests** (no LLM/API). The other commands call the **actual LangGraph graph** and your configured LLMs, which can incur costs and produce different outputs on different runs. The command exits nonzero when some case fails, but still writes reports to `reports/evaluation/results.json` and `reports/evaluation/summary.md`.

The current checks are intentionally deterministic: exactly one critique per dimension, scores within expected ranges, issue **dimension + severity** present for expected mandatory issues, no issues for zero-issue baseline cases, and a valid verdict. The runner **does not** compare issue descriptions semantically, does not independently verify facts, and does not test expected adjudication dispositions for private/unverifiable claims. These are good next steps for LLM-as-a-Judge evaluation. A `PASS` here does not mean semantic correctness has been established.

The 16-case dataset is in `tests/evaluation/dataset.json` and contains subjective ranges; review and refine them based on your critic rubrics. The runner intentionally does not modify any existing prompts, nodes, or State.
