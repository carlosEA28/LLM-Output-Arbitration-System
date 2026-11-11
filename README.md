# LLM Output Arbitration System

The Python application, tests, and configuration live in [`backend/`](backend/).

To install dependencies and start the API:

```bash
cd backend
uv sync --frozen
uv run uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Check the server with `curl http://127.0.0.1:8000/health`. See the [backend README](backend/README.md) for setup, API usage, tests, CLI, and Docker Compose instructions.
