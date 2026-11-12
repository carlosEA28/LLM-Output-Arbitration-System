# Design

## Context

Veja `proposal.md` para a motivação e `specs/critic-analytics/spec.md` para o contrato. Hoje `src/api/arbitration_history.py` usa SQLite com uma linha por execução, `status` de execução e `evaluation_json` opcional. A avaliação já contém `critiques`, `requires_adjudication`, `adjudication` e `verdict`; `src/api/main.py` registra rotas FastAPI síncronas. Apenas `POST /generate-and-evaluate` persiste avaliações. A leitura do banco é configurada por `ARBITRATION_DB_PATH`.

## Goals / Non-Goals

**Goals:** Calcular métricas a partir de um conjunto consistente dos registros existentes, com rota de leitura pequena, schema Pydantic explícito e testes isolados por banco temporário. Preservar o fluxo e os contratos de geração e avaliação.

**Non-Goals:** Persistir `/evaluate` ou avaliações de lote, criar armazenamento de métricas, recomputar histórico, expor registros individuais ou adicionar infraestrutura.

## Decisions

1. **Fonte dos dados:** adicionar uma função de leitura em `src/api/arbitration_history.py` que selecione `status` e `evaluation_json` da tabela atual em uma conexão curta. O serviço de analytics percorre os registros uma vez e só interpreta avaliações de linhas `completed`. Isso reutiliza a conexão e o caminho de banco existentes sem novo repositório, tabela ou dependência. A alternativa de funções SQL JSON específicas do SQLite exigiria depender da disponibilidade dessa extensão e complicaria o tratamento das listas aninhadas.
2. **Semântica das contagens:** `total` inclui todas as linhas, inclusive `pending`, `failed` e `timed_out`. `assessed` e `inconclusive` são valores de `evaluation.verdict.status`, não do status de execução. Cada objeto em `critiques` conta uma avaliação da dimensão indicada; a média é soma dos scores dividida pelo número de críticas dessa dimensão, com zero quando não há críticas. `requested` usa `requires_adjudication`, independentemente de `adjudication` ser nula; issues confirmados e descartados vêm somente de `adjudication`, evitando misturar decisões finais do veredito com decisões da adjudicação. Alternativas de contar apenas execuções completas em `total` ou usar listas do veredito mudariam o significado dos dados pedidos.
3. **Camadas da API:** um serviço pequeno em `src/api/services/` calcula os agregados, um schema de transporte em `src/api/schemas/responses.py` fixa o formato, e uma rota síncrona `GET /v1/analytics` registrada em `src/api/main.py` delega ao serviço. A rota captura falhas de armazenamento ou leitura com HTTP 500 genérico, seguindo o padrão das rotas existentes. Não inicializa provedores nem chama o grafo. Uma rota assíncrona que lê SQLite diretamente bloquearia o event loop.
4. **Resposta vazia:** inicializar no serviço as três dimensões e todas as contagens com zero antes de ler linhas. `average_score` é número de ponto flutuante, inclusive `0.0` quando o denominador é zero. A leitura da conexão existente pode criar a tabela atual na primeira consulta a um banco ainda inexistente; isso não cria estrutura nova nem grava avaliações.

## Risks / Trade-offs

- [A agregação lê os resultados persistidos a cada requisição] → Aceitar o custo proporcional ao tamanho do histórico nesta versão básica; não adicionar cache ou tabela de resumo.
- [Uma avaliação persistida corrompida impede cálculo confiável] → Falhar com resposta HTTP 500 genérica, sem expor conteúdo do banco; não inventar valores nem alterar registros.
- [Execuções de avaliação direta e lote não aparecem] → Documentar que as métricas cobrem apenas o histórico persistido pelo fluxo de pergunta.

## Migration Plan

Nenhuma migração. Implantar a nova rota com o mesmo arquivo SQLite e a mesma variável `ARBITRATION_DB_PATH`. A reversão do código remove somente a consulta; os registros existentes permanecem intactos.
