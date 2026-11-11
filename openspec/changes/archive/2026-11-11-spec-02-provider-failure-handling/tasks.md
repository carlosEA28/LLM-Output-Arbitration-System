# Tasks

## 1. Classificação e retries dos críticos

- [ ] 1.1 Ajustar `_failure_category` em `src/nodes/critics.py` para tipos Google diretos/encadeados e códigos 429, 5xx, 408, 401/403 e 4xx, além de timeout/conexão/configuração; verificar com testes de tabela em `tests/test_critic_retries.py`, incluindo `GoogleRateLimitError` sem causa e `GoogleAPIError` permanente.
- [ ] 1.2 Manter no máximo duas invocações com backoff limitado e desativar retry interno sobreposto (`max_retries=1` no Gemini, zero no OpenAI); verificar por testes offline de recuperação, falha persistente, erro permanente e contagem exata de chamadas/esperas.

## 2. Diagnóstico no estado e cobertura

- [ ] 2.1 Adicionar `critic_diagnostics` ao estado agregado e emitir um registro seguro por crítico, com dimensão, provedor, status, categoria e tentativas, preservando `failed_critics`; verificar com testes dos três críticos que mensagens contendo segredo não entram no estado nem nos logs.
- [ ] 2.2 Atualizar testes do grafo/veredito para confirmar que falha isolada de Gemini preserva as outras duas críticas e produz cobertura 2/3 e veredito inconclusivo; verificar com `uv run pytest tests/test_critic_retries.py tests/test_graph_routing.py tests/test_synthesize_verdict.py` sem LLM.

## 3. Runner e relatórios

- [ ] 3.1 Ler somente campos permitidos de `critic_diagnostics` no runner e apresentar categoria/tentativas no JSON e no Markdown de caso inconclusivo; verificar em `tests/evaluation/test_evaluate.py` que rate limit de lógica não vira falha de qualidade e que estados antigos sem diagnóstico continuam legíveis.
- [ ] 3.2 Implementar `--case-id` repetível, aplicação posterior de `--limit` e `--interval-seconds` finito/não negativo, com espera só entre casos; verificar testes de seleção, ID desconhecido, limite, intervalo e ausência de espera após o último caso.
- [ ] 3.3 Recusar destino com `results.json` ou `summary.md` antes de construir o grafo, salvo `--overwrite`, e documentar reexecução em diretório novo em `tests/README_EVALUATION.md`; verificar com teste offline que o baseline existente não muda e que a saída nova contém só os IDs selecionados.

## 4. Integração

- [ ] 4.1 Executar a suíte offline de críticos, grafo, veredito e avaliação, além de `openspec validate spec-02-provider-failure-handling --strict`; verificar saída sem falhas e criar o commit `fix(llm): handle provider failures and bounded retries`.
