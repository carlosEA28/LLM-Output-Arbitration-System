# Spec Delta

## Purpose

Disponibiliza uma visão agregada das arbitragens persistidas para acompanhar resultados dos críticos e decisões de adjudicação sem reexecutar avaliações.

## ADDED Requirements

### Requirement: Consultar métricas básicas pela API
`GET /v1/analytics` SHALL retornar HTTP 200 com um objeto JSON composto por `arbitrations`, `critics` e `adjudication`, usando campos numéricos para todas as métricas. A consulta MUST usar somente resultados persistidos e MUST NOT executar modelos.

#### Scenario: Consulta com histórico existente
- **WHEN** o cliente solicita `GET /v1/analytics` após arbitragens terem sido persistidas
- **THEN** recebe as métricas agregadas atuais sem criar uma nova arbitragem ou executar LLMs

#### Scenario: Banco vazio
- **WHEN** não há arbitragens persistidas
- **THEN** recebe HTTP 200 com todas as contagens e médias iguais a zero e entradas para as três dimensões

### Requirement: Contar arbitragens e status do veredito
`arbitrations` SHALL conter `total`, `assessed` e `inconclusive`. `total` SHALL contar todos os registros persistidos; `assessed` e `inconclusive` SHALL contar somente avaliações concluídas cujo `verdict.status` tenha o valor correspondente.

#### Scenario: Execuções com status distintos
- **WHEN** há registros `pending`, `failed`, `timed_out` e `completed`, incluindo um veredito `inconclusive`
- **THEN** todos entram em `total`, mas somente os registros `completed` entram no subtotal de seu respectivo status de veredito

### Requirement: Agregar avaliações por dimensão
`critics` SHALL conter `accuracy`, `logic` e `completeness`, cada qual com `evaluations`, `average_score` e `issues`. Cada crítica persistida de uma avaliação concluída SHALL contar uma avaliação, contribuir com seu score para a média de sua dimensão e acrescentar o tamanho de sua lista de issues ao total.

#### Scenario: Avaliações parciais e repetidas
- **WHEN** avaliações concluídas têm dimensões ausentes ou mais de uma crítica da mesma dimensão
- **THEN** somente as críticas presentes contribuem, e cada crítica presente é contada separadamente na sua dimensão

#### Scenario: Dimensão sem crítica
- **WHEN** uma dimensão não aparece em nenhuma avaliação concluída
- **THEN** seus valores `evaluations`, `average_score` e `issues` são zero

### Requirement: Agregar adjudicação
`adjudication` SHALL conter `requested`, `confirmed_issues` e `dismissed_issues`. `requested` SHALL contar avaliações concluídas com `requires_adjudication=true`; os totais de issues SHALL usar as listas `confirmed_issues` e `dismissed_issues` da adjudicação persistida, quando presente.

#### Scenario: Adjudicação solicitada com decisões
- **WHEN** uma avaliação concluída solicitou adjudicação e tem listas de issues confirmados e descartados
- **THEN** `requested` aumenta em um e cada lista contribui com seu número de itens ao total correspondente

#### Scenario: Solicitação sem adjudicação persistida
- **WHEN** uma avaliação concluída tem `requires_adjudication=true` e `adjudication=null`
- **THEN** ela contribui para `requested`, mas não para os totais de issues adjudicados
