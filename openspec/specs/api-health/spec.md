# api-health Specification

## Purpose

Provides a lightweight HTTP signal that the API application is reachable without relying on the arbitration pipeline or external model providers.

## Requirements

### Requirement: Health endpoint responds successfully
The API SHALL expose `GET /health` and return HTTP 200 for a valid request.

#### Scenario: Request health status
- **WHEN** a client sends `GET /health`
- **THEN** the API returns HTTP 200

### Requirement: Health check is independent of LLMs
The API SHALL serve `GET /health` without initializing a model provider or making an LLM call.

#### Scenario: Health request without model access
- **WHEN** a client sends `GET /health` while no model provider is configured or reachable
- **THEN** the API returns HTTP 200 without attempting provider initialization or an LLM call
