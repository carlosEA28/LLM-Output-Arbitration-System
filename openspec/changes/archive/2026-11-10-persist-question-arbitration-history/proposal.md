# Proposal

## Why

`POST /generate-and-evaluate` entrega um veredito, mas o resultado desaparece após a resposta HTTP. Persistir cada solicitação válida desse fluxo permite recuperar avaliações e identificar execuções que falharam.

## What Changes

- Atribuir um ID único e data de criação a cada solicitação válida de `POST /generate-and-evaluate` e registrar seu status de execução em SQLite.
- Persistir pergunta, resposta gerada quando disponível, críticas e veredito quando a avaliação termina, incluindo vereditos inconclusivos; registrar falhas e timeouts sem salvar detalhes internos de exceções.
- Acrescentar o ID à resposta bem-sucedida e disponibilizá-lo por cabeçalho também em respostas de falha, preservando os corpos de erro existentes.
- Expor `GET /v1/arbitrations/{id}` para recuperar o registro ou retornar 404 quando ele não existir.
- Manter `POST /evaluate` sem persistência ou mudança de contrato.

## Capabilities

### New Capabilities

- `arbitration-history`: armazenamento e consulta por ID de execuções iniciadas pelo fluxo de pergunta apenas.

### Modified Capabilities

- `api-generation`: a resposta do fluxo de pergunta passa a fornecer um ID consultável, inclusive quando a execução falha.

## Impact

Afeta o adaptador FastAPI, seus schemas de transporte, um pequeno componente de persistência SQLite, testes de API e configuração local do arquivo de dados. Não altera o grafo, os críticos, o gerador, os schemas de domínio ou `POST /evaluate`. Usa `sqlite3` da biblioteca padrão, sem PostgreSQL, ORM ou migrações genéricas.
