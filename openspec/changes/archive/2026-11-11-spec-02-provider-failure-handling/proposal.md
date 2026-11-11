# Proposal

## Why

Falhas do Gemini podem deixar `logic` sem crítica; hoje o estado expõe só o nome do crítico com falha, sem categoria ou tentativas. Além disso, o cliente Google instalado aceita `max_retries`, enquanto o código passa `retries`, o que pode manter tentativas internas não previstas e somá-las ao retry externo.

## What Changes

- Classificar falhas por tipo e código observáveis: limite de taxa, 5xx, timeout/conexão e erros permanentes de autenticação, permissão ou requisição.
- Aplicar retries transitórios com limite e backoff explícitos, sem retries internos sobrepostos; não repetir falhas permanentes.
- Propagar diagnóstico seguro por crítico, com dimensão, provedor, categoria e tentativas, preservando `failed_critics` e as críticas válidas das demais dimensões.
- Exibir o diagnóstico operacional nos relatórios da SPEC-01 e manter casos com dimensão ausente como inconclusivos.
- Permitir selecionar casos para reexecução, limitar volume, configurar intervalo entre casos e proteger relatórios existentes contra sobrescrita acidental.
- **BREAKING:** uma execução que tenta gravar em um diretório com relatórios existentes exigirá `--overwrite` ou um novo `--output`.

## Capabilities

### New Capabilities

- `provider-failure-handling`: Classificação, tentativas limitadas e preservação de resultados parciais dos críticos LLM.

### Modified Capabilities

- `evaluation-reporting`: Diagnóstico operacional detalhado e reexecução seletiva sem sobrescrever relatórios existentes.

## Impact

- Críticos e estado em `src/nodes/critics.py` e `src/arbitration/states.py`; testes de retry, grafo e veredito.
- Runner e documentação em `tests/evaluation/evaluate.py`, `tests/evaluation/test_evaluate.py` e `tests/README_EVALUATION.md`.
- Sem troca de provedor, alteração de prompts, pontuação dos críticos, arquitetura de roteamento, adjudicador, filas ou dataset de referência.
