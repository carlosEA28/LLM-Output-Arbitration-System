# evaluation-reporting Specification

## Purpose

Define o contrato dos relatórios do Evaluation Runner para que cada execução possa ser auditada e falhas operacionais sejam separadas de divergências de qualidade.

## Requirements

### Requirement: Diagnóstico de execução por caso
O relatório JSON SHALL registrar, para cada caso, `case_id`, `elapsed_seconds`, `execution_status` (`success`, `partial` ou `error`), `failed_critics`, contagem de críticas por dimensão, diagnóstico seguro de cada crítico (dimensão, provedor, categoria quando houver e tentativas) e motivo operacional quando disponível. O relatório MUST omitir segredos e chaves de API.

#### Scenario: Execução completa
- **WHEN** o grafo retorna uma crítica para cada dimensão necessária, sem falhas de críticos e com verdict válido
- **THEN** o caso apresenta `execution_status: success`, três contagens iguais a 1 e lista vazia de críticos com falha

#### Scenario: Crítico indisponível
- **WHEN** o grafo retorna `failed_critics` com `logic_critic` e nenhuma crítica de `logic`
- **THEN** o caso apresenta `execution_status: partial`, contagem 0 em `logic` e motivo operacional que identifica o crítico indisponível

#### Scenario: Exceção inesperada
- **WHEN** a invocação do grafo lança uma exceção
- **THEN** o caso apresenta `execution_status: error`, duração e tipo da exceção como motivo seguro, sem depender da mensagem bruta da exceção

#### Scenario: Falha de provedor rastreável
- **WHEN** um crítico falha por limite de taxa após o número máximo de tentativas
- **THEN** JSON e Markdown identificam dimensão, provedor, `rate_limit` e tentativas sem atribuir a falha à qualidade do conteúdo

### Requirement: Separação entre execução e qualidade
O relatório SHALL registrar `evaluation_pass` como booleano para casos avaliáveis e `null` para casos não avaliáveis. Um caso MUST ser não avaliável quando faltar uma dimensão necessária ou o grafo não produzir resultado utilizável; falhas operacionais MUST NOT contar como reprovação de qualidade.

#### Scenario: Falha operacional do Logic Critic
- **WHEN** `logic_critic` falha, inclusive por `GoogleRateLimitError`, e a dimensão `logic` não é retornada
- **THEN** `evaluation_pass` é `null` e o caso é inconclusivo, sem atribuir baixa qualidade à avaliação lógica

#### Scenario: Divergência de qualidade avaliável
- **WHEN** todas as dimensões necessárias são retornadas uma vez e um score fica fora da faixa esperada
- **THEN** `evaluation_pass` é `false` e o motivo identifica dimensão, score observado e faixa esperada

### Requirement: Resultado auditável por expectativa
O relatório SHALL preservar scores e issues observados, incluindo dimensão, severidade e descrição, e SHALL registrar o resultado e o motivo de cada expectativa obrigatória. A verificação de issues SHALL continuar baseada em presença de dimensão e severidade, sem afirmar correspondência semântica de descrições.

#### Scenario: Severidade diferente na mesma dimensão
- **WHEN** um issue observado tem a dimensão esperada, mas severidade diferente
- **THEN** o motivo mostra a dimensão, a severidade esperada, a severidade observada e a descrição do issue, em vez de apenas `0 candidate(s)`

#### Scenario: Score de eval_003
- **WHEN** o relatório contém o resultado observado de `eval_003` com `accuracy` igual a 1
- **THEN** o diagnóstico mostra `accuracy` observado 1 e faixa esperada 4–5

### Requirement: Resumo com denominador explícito
Os relatórios JSON e Markdown SHALL informar total de casos, aprovados, reprovados por qualidade, inconclusivos e taxa de aprovação calculada como aprovados divididos pelos casos avaliáveis. O Markdown SHALL apresentar status e motivo individual para casos reprovados ou inconclusivos.

#### Scenario: Amostra com falha operacional
- **WHEN** há um caso aprovado, um reprovado por qualidade e um inconclusivo
- **THEN** os relatórios mostram 1 aprovado, 1 reprovado, 1 inconclusivo, 2 casos avaliáveis e taxa de aprovação de 50%

#### Scenario: Nenhum caso avaliável
- **WHEN** todos os casos são inconclusivos
- **THEN** o denominador avaliável é 0 e os relatórios não apresentam divisão por zero nem atribuem uma taxa de qualidade enganosa

### Requirement: Compatibilidade dos dados existentes
O JSON SHALL manter os campos atuais de caso e os detalhes de `checks`, `observed_scores`, `observed_issues`, `verdict`, `adjudication` e `requires_adjudication` quando disponíveis. O campo legado `passed` SHALL permanecer booleano e refletir `evaluation_pass is true`; consumidores SHALL usar `evaluation_pass` para distinguir inconclusão de reprovação.

#### Scenario: Leitura de caso inconclusivo
- **WHEN** um consumidor lê um caso com falha operacional
- **THEN** `passed` é `false`, `evaluation_pass` é `null` e `execution_status` identifica a falha operacional

### Requirement: Reexecução seletiva sem sobrescrita acidental
O Evaluation Runner SHALL permitir selecionar casos por `case_id`, manter limite de casos e aceitar intervalo não negativo entre casos. Ao encontrar relatórios existentes no destino, MUST recusar sobrescrita sem opção explícita de substituição; uma reexecução seletiva SHALL poder gravar em destino novo sem alterar o baseline anterior.

#### Scenario: Reexecutar casos afetados
- **WHEN** o operador seleciona um ou mais IDs existentes e um diretório de saída novo
- **THEN** somente esses casos são executados e os relatórios anteriores permanecem intactos

#### Scenario: Destino com relatórios existentes
- **WHEN** o destino contém `results.json` ou `summary.md` e não há autorização explícita de substituição
- **THEN** o runner encerra antes de invocar o grafo e indica como escolher outro destino ou autorizar a substituição

#### Scenario: Limite e intervalo
- **WHEN** o operador define limite de casos e intervalo positivo
- **THEN** o runner executa no máximo o limite solicitado e espera somente entre casos selecionados
