# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
