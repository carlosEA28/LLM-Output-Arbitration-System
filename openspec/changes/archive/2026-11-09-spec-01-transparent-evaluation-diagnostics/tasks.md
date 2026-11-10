# Tasks

## 1. Contrato e classificação

- [x] 1.1 Registrar no código ou em comentário de contrato os campos atuais de `evaluate.py`, `dataset.json`, `results.json` e do estado do grafo; verificar com fixtures que os campos legados do caso continuam presentes no JSON gerado.
- [x] 1.2 Implementar `execution_status`, `case_id`, `failed_critics`, contagens por dimensão, duração e motivo seguro para retorno completo, parcial e exceção; verificar com testes offline de grafo simulado para os três status, inclusive ausência de `logic`.
- [x] 1.3 Calcular `evaluation_pass` separadamente, com `null` em falha operacional, e preservar `passed` legado; verificar com testes offline que `GoogleRateLimitError` capturado como falha de `logic_critic` gera inconclusão e que score fora da faixa gera reprovação de qualidade.

## 2. Diagnóstico das expectativas

- [x] 2.1 Preservar `observed_scores` e `observed_issues` e enriquecer checks com esperado/observado por dimensão; verificar em teste que `eval_003` exibe `accuracy` 1 contra faixa 4–5.
- [x] 2.2 Detalhar checks de issue com dimensão, severidade e descrição observadas quando a expectativa não coincidir; verificar com teste offline de severidade diferente e manter explícito que o significado da descrição não é comparado.

## 3. Relatórios e integração

- [x] 3.1 Atualizar a agregação JSON para `passed`, `failed`, `inconclusive`, `evaluable` e `pass_rate` sobre avaliáveis; verificar com teste misto e teste com zero avaliáveis que a taxa não divide por zero.
- [x] 3.2 Atualizar `summary.md` e a saída CLI para mostrar classificação, motivo individual e score/severidade divergente; verificar em teste offline o conteúdo dos dois arquivos e o código de saída da CLI.
- [x] 3.3 Executar `uv run pytest tests/evaluation/test_evaluate.py` e validar o change com `openspec validate spec-01-transparent-evaluation-diagnostics --strict`; verificar ambos com saída sem erros e registrar no commit `feat(eval): add execution diagnostics and detailed reports`.
