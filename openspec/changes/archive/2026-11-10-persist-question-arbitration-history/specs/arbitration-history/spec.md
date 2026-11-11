# Spec Delta

## Purpose

Permite recuperar por identificador o resultado ou o status de uma execução iniciada pelo fluxo HTTP de pergunta apenas, inclusive após reiniciar a aplicação.

## ADDED Requirements

### Requirement: Registrar execuções válidas do fluxo de pergunta
Cada solicitação válida a `POST /generate-and-evaluate` SHALL criar um registro persistente com ID único, pergunta, data de criação em UTC e status de execução. `POST /evaluate` e solicitações rejeitadas com HTTP 422 MUST NOT criar registros.

#### Scenario: Solicitação válida
- **WHEN** o cliente envia uma pergunta válida ao fluxo de geração e avaliação
- **THEN** o registro recebe ID único, a pergunta original, data de criação e status inicial `pending`

#### Scenario: Entrada inválida ou avaliação direta
- **WHEN** a API rejeita uma pergunta com HTTP 422 ou recebe `POST /evaluate`
- **THEN** nenhum registro de histórico é criado por essa solicitação

### Requirement: Preservar resultados concluídos
Ao concluir a geração e a avaliação, o registro SHALL guardar a resposta gerada e o resultado estruturado da avaliação, incluindo críticas, diagnósticos, adjudicação opcional e veredito, sem alterar os valores produzidos pelo grafo. O status de execução SHALL ser `completed` mesmo quando o veredito for `inconclusive`.

#### Scenario: Avaliação concluída
- **WHEN** o fluxo gera uma resposta e produz um veredito válido
- **THEN** o registro fica `completed` e contém a pergunta, a resposta e o resultado estruturado retornado pela API

#### Scenario: Veredito inconclusivo válido
- **WHEN** o grafo produz um veredito válido com `status: inconclusive`
- **THEN** o registro fica `completed` e preserva o veredito e as críticas ou diagnósticos disponíveis

### Requirement: Registrar falhas sem detalhes internos
Se uma solicitação válida terminar em HTTP 500 ou 504, o registro SHALL ficar `failed` ou `timed_out`, respectivamente. Ele SHALL preservar a pergunta e a resposta gerada quando disponível, mas MUST NOT persistir texto de exceções, credenciais, prompts internos ou payloads de provedores.

#### Scenario: Falha na geração
- **WHEN** a geração falha antes de produzir resposta válida
- **THEN** o registro fica `failed` ou `timed_out`, sem resposta gerada nem resultado de avaliação

#### Scenario: Falha depois da geração
- **WHEN** a avaliação falha depois que a resposta foi gerada
- **THEN** o registro preserva a resposta gerada e fica `failed` ou `timed_out`, sem veredito inválido nem detalhes internos

### Requirement: Consultar histórico por ID
`GET /v1/arbitrations/{id}` SHALL retornar HTTP 200 com `id`, `status`, `created_at`, `original_question`, `generated_output` e `evaluation`. `generated_output` e `evaluation` SHALL ser nulos quando indisponíveis; `evaluation` SHALL conter o resultado estruturado completo quando a execução estiver `completed`.

#### Scenario: ID existente
- **WHEN** o cliente consulta um ID de execução existente, inclusive após reiniciar a aplicação
- **THEN** a API retorna o registro persistido com os campos disponíveis e o status de execução

#### Scenario: ID desconhecido
- **WHEN** o cliente consulta um ID válido que não existe
- **THEN** a API retorna HTTP 404

#### Scenario: ID malformado
- **WHEN** o cliente fornece um ID fora do formato aceito
- **THEN** a API retorna HTTP 422 sem consultar registros
