# Design

## Context

O runner em `tests/evaluation/evaluate.py` recebe o estado final de `graph.invoke` e compara scores e presença de issues por dimensão/severidade. O JSON atual já contém `id`, `scenario`, `passed`, `checks`, `observed_scores`, `observed_issues`, `verdict`, `adjudication`, `requires_adjudication` e `elapsed_seconds`; o Markdown exibe apenas PASS/FAIL e checks falhos. O dataset fornece `id`, faixas de `expected_scores` e `expected_issues` com `dimension`, `severity`, descrição e eventual `optional`.

O estado do grafo contém `critiques`, `failed_critics`, `missing_dimensions`, `duplicate_dimensions`, `critiques_complete` e `verdict`. Cada falha capturada internamente pelo crítico acrescenta apenas seu nome a `failed_critics`; a categoria e a exceção são emitidas ao logger, mas não retornam no estado. Ver `proposal.md` e `specs/evaluation-reporting/spec.md`.

## Goals / Non-Goals

**Goals:**

- Derivar um diagnóstico por caso exclusivamente da resposta do grafo e da exceção que chegar ao runner.
- Manter os campos existentes e acrescentar status e métricas explícitos, evitando interpretar erro operacional como score ruim.
- Gerar JSON e Markdown a partir de uma mesma classificação, com detalhes seguros para publicação.

**Non-Goals:**

- Instrumentar o interior dos críticos, alterar logging, retries, prompts, adjudicação, roteamento ou dataset.
- Inferir correspondência semântica entre descrições de issues esperados e observados.

## Decisions

### Classificação única por caso

Calcular contagens de `critiques` por dimensão e usar `failed_critics`, dimensões ausentes/duplicadas e presença de verdict para classificar o resultado. `success` exige exatamente uma crítica por dimensão, nenhum crítico com falha e verdict válido. `partial` indica que o grafo retornou um estado, mas alguma dessas condições não foi satisfeita. `error` indica exceção propagada por `graph.invoke` ou impossibilidade de interpretar seu retorno. Somente `success` é avaliável; nesse caso `evaluation_pass` agrega os checks de qualidade. Em `partial`/`error`, `evaluation_pass` é `null`, mas checks aplicáveis e dados parciais continuam disponíveis para diagnóstico. O booleano legado `passed` é verdadeiro somente se `evaluation_pass` for verdadeiro.

Alternativa considerada: tratar cada check falho como reprovação. Isso mantém a ambiguidade atual e atribui falhas do provedor à qualidade do crítico.

### Motivo operacional seguro

Para `failed_critics`, registrar os nomes retornados pelo grafo e uma razão como “crítico sem resposta; causa não disponível no estado”. Não inferir `GoogleRateLimitError` do nome `logic_critic`. Para exceções propagadas, registrar o nome da classe e uma razão controlada, sem interpolar `str(exc)`, payloads, estado de entrada nem configuração. Assim um rate limit capturado aparece como falha operacional mesmo quando a classe exata não está no estado.

Alternativa considerada: capturar logs ou alterar o contrato dos críticos para transportar exceções. Isso amplia o escopo e pode expor mensagens de provedor com dados sensíveis.

### Checks detalhados sem julgamento semântico

Preservar nomes e formato básico de `checks`. Acrescentar campos estruturados de esperado/observado onde cabível; os detalhes textuais terão score e faixa ou, para issues, a dimensão/severidade esperadas e os issues observados na dimensão com severidade e descrição. Quando não houver issue na dimensão, indicar ausência; quando houver issue em outra dimensão, mostrar sua dimensão. Issues opcionais continuam sem check obrigatório. Os campos `observed_scores` e `observed_issues` permanecem.

Alternativa considerada: comparar descrições por texto ou similaridade. Isso mudaria o método de avaliação e poderia criar falsos positivos.

### Agregação e renderização

Derivar `passed`, `failed`, `inconclusive` e `evaluable` da classificação de cada caso; `pass_rate` será `passed/evaluable` e `null` quando `evaluable` for zero. O Markdown exibirá esse denominador, a distribuição de status e os motivos de cada caso reprovado/inconclusivo. A CLI mostrará a mesma distribuição e terminará com código 0 somente se todos os casos forem avaliáveis e aprovados. `total`, `created_at`, `evaluation_method` e `cases` continuam disponíveis.

Alternativa considerada: manter `pass_rate` sobre o total. Isso mistura confiabilidade da execução com qualidade e contraria o critério de aceite.

## Risks / Trade-offs

- [Causa interna de crítico indisponível não chega ao runner] → mostrar explicitamente que a causa detalhada não está disponível, mantendo `failed_critics` e dimensão ausente.
- [Consumidores interpretam `passed: false` como reprovação de qualidade] → preservar o campo por compatibilidade, documentar `evaluation_pass`/`execution_status` e separar contagens agregadas.
- [Markdown contém texto de issue retornado por provedor] → limitar o texto aos campos de issue já presentes no JSON e escapar caracteres de formatação relevantes ao renderizar tabelas/listas.
- [Relatórios antigos possuem `pass_rate` calculado sobre o total] → explicitar `evaluable` no novo relatório e não reinterpretar arquivos já gerados.

## Migration Plan

Gerar relatórios novos pelo runner atualizado, sem migração dos arquivos históricos. Validar os cenários offline antes de uma execução real; manter os relatórios de referência existentes intactos durante a implementação. Para reverter, restaurar o runner anterior e regenerar os relatórios quando necessário.
