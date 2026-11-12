# Proposal

## Why

O histórico já armazena arbitragens e avaliações estruturadas, mas a API só permite consultar cada execução por ID. Métricas agregadas ajudam a observar o comportamento dos críticos e da adjudicação com os dados que já existem.

## What Changes

- Adicionar `GET /v1/analytics` com totais de arbitragens, vereditos `assessed` e `inconclusive`.
- Agregar, para `accuracy`, `logic` e `completeness`, quantidade de avaliações, score médio e quantidade de issues relatados.
- Agregar solicitações de adjudicação e issues confirmados ou descartados pela adjudicação.
- Retornar um schema Pydantic com valores numéricos zerados quando não houver avaliações; cobrir os cálculos e o endpoint com testes sem executar LLMs.

## Capabilities

### New Capabilities

- `critic-analytics`: consulta HTTP de métricas agregadas das arbitragens persistidas.

### Modified Capabilities

Nenhuma. O histórico e o pipeline mantêm seus contratos atuais.

## Impact

- API FastAPI: nova rota e schema de resposta; leitura agregada do SQLite existente por um serviço pequeno.
- Persistência: apenas consulta à tabela `arbitrations` e ao `evaluation_json` já gravado, sem tabela ou migração.
- Testes: casos de cálculos, banco vazio e resposta HTTP.
- Nenhuma dependência nova; nenhum ajuste no grafo, nos críticos, prompts ou schemas de arbitragem.
