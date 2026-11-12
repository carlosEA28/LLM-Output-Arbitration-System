# Tasks

## 1. Leitura e agregação

- [x] 1.1 Adicionar em `backend/src/api/arbitration_history.py` uma leitura curta de `status` e `evaluation_json` pelo banco existente; verificar com teste usando `ARBITRATION_DB_PATH` temporário que linhas de estados distintos são recuperadas sem alterar o histórico.
- [x] 1.2 Implementar o serviço de analytics com contagens, médias e adjudicação conforme o spec; verificar com testes de múltiplas avaliações, avaliações parciais, adjudicação nula e banco vazio, sem chamadas a LLMs.

## 2. Contrato HTTP

- [x] 2.1 Adicionar schema Pydantic de resposta e rota síncrona `GET /v1/analytics` registrada na aplicação; verificar com `TestClient` o JSON e HTTP 200 para banco populado e vazio, além de HTTP 500 genérico para falha de leitura.

## 3. Verificação integrada

- [x] 3.1 Executar os novos testes e os testes de regressão relevantes da API e persistência com `uv run pytest`; registrar os resultados reais e verificar que nenhum teste exige chamadas pagas a modelos.
