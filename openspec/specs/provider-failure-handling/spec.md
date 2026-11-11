# provider-failure-handling Specification

## Purpose

Define como os críticos LLM classificam falhas de provedores, limitam tentativas e preservam resultados parciais para que a avaliação permaneça auditável.

## Requirements

### Requirement: Classificação explícita de falhas
Cada crítico SHALL classificar a falha observada pela exceção tipada e, quando houver, pelo código de status. O sistema MUST distinguir `rate_limit`, `server_error`, `timeout`, `connection`, `authentication`, `invalid_request`, `configuration`, `invalid_evaluation` e `call_error`; uma exceção genérica MUST NOT ser presumida transitória.

#### Scenario: Rate limit do Gemini
- **WHEN** o provedor retorna código 429 ou uma exceção tipada de limite de taxa, com ou sem causa encadeada
- **THEN** o diagnóstico identifica `rate_limit` como falha operacional do crítico afetado

#### Scenario: Erro de servidor e timeout
- **WHEN** o provedor retorna código 5xx ou ocorre timeout/conexão
- **THEN** a categoria é respectivamente `server_error`, `timeout` ou `connection`

#### Scenario: Erro permanente
- **WHEN** o provedor retorna 401, 403 ou erro de requisição/payload inválido
- **THEN** a categoria é `authentication` ou `invalid_request`, sem tratar o erro como transitório

#### Scenario: Configuração inválida
- **WHEN** a construção do cliente falha por configuração inválida antes da chamada ao modelo
- **THEN** a categoria é `configuration` e o diagnóstico registra zero invocações do modelo

### Requirement: Tentativas limitadas por crítico
Cada crítico SHALL realizar no máximo duas invocações efetivas do modelo por avaliação. Somente `rate_limit`, `server_error`, `timeout` e `connection` SHALL permitir uma segunda tentativa após espera limitada; erros permanentes MUST encerrar após a primeira. Retentativas internas do cliente MUST NOT ampliar esse limite.

#### Scenario: Rate limit recuperável
- **WHEN** a primeira invocação falha por limite de taxa e a segunda retorna uma crítica válida
- **THEN** a crítica é preservada e o diagnóstico registra duas tentativas

#### Scenario: Falha persistente
- **WHEN** as duas invocações permitidas falham por erro transitório
- **THEN** o crítico termina com falha após duas tentativas e não entra em novo ciclo

#### Scenario: Credencial inválida
- **WHEN** a primeira invocação falha por autenticação
- **THEN** o crítico termina com uma tentativa, sem espera de retry

### Requirement: Diagnóstico seguro e estado parcial
O estado da avaliação SHALL manter `failed_critics` e registrar para cada crítico sua dimensão, provedor, categoria de falha quando houver e número de tentativas. Diagnósticos e logs MUST NOT conter token, chave, mensagem bruta de exceção ou payload sensível; uma falha de um crítico MUST NOT descartar críticas válidas dos outros.

#### Scenario: Falha isolada do Logic Critic
- **WHEN** o crítico de lógica falha e os críticos de accuracy e completeness retornam críticas válidas
- **THEN** `failed_critics` inclui lógica, o diagnóstico informa provedor/categoria/tentativas e as outras duas críticas permanecem no estado

#### Scenario: Crítico recuperado
- **WHEN** um crítico retorna uma crítica válida após uma segunda tentativa
- **THEN** o diagnóstico registra duas tentativas e o crítico não consta em `failed_critics`

### Requirement: Veredito com cobertura correta
O veredito SHALL permanecer inconclusivo quando faltar uma dimensão ou houver crítico com falha, e SHALL indicar a cobertura real sem tratar a avaliação parcial como completa.

#### Scenario: Uma dimensão ausente
- **WHEN** somente duas dimensões retornam críticas e a terceira falha
- **THEN** o veredito é inconclusivo e informa cobertura de duas entre três dimensões
