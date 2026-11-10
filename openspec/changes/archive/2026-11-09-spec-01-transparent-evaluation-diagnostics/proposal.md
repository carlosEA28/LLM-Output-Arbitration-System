# Proposal

## Why

O Evaluation Runner atualmente resume resultados em PASS/FAIL e mistura indisponibilidade de críticos com divergências de qualidade. Isso torna impossível auditar, pelo relatório, se uma expectativa falhou por resposta do crítico, por severidade diferente ou por falha operacional.

## What Changes

- Registrar por caso o status de execução (`success`, `partial`, `error`), críticos com falha, contagem de críticas por dimensão, duração e motivo operacional disponível.
- Separar `evaluation_pass` da execução, usando `null` para casos não avaliáveis por ausência de dimensão necessária ou erro operacional.
- Preservar scores, issues, verdict e checks existentes no JSON, acrescentando diagnóstico estruturado e motivos específicos para score, dimensão e severidade.
- Ampliar `summary.md` com contagens de aprovados, reprovados por qualidade e inconclusivos, taxa de aprovação sobre casos avaliáveis e detalhes individuais.
- Cobrir os caminhos com testes determinísticos, sem chamadas a LLM.

## Capabilities

### New Capabilities

- `evaluation-reporting`: Contrato de diagnóstico e apresentação dos resultados do Evaluation Runner.

### Modified Capabilities

Nenhuma. O projeto ainda não possui specs principais.

## Impact

- `tests/evaluation/evaluate.py` e `tests/evaluation/test_evaluate.py`.
- Arquivos gerados `reports/evaluation/results.json` e `reports/evaluation/summary.md`.
- Compatibilidade dos campos atuais do relatório JSON sempre que possível; métricas agregadas passam a distinguir casos avaliáveis de inconclusivos.
- Sem alteração de prompts, scores dos críticos, política de retry, adjudicador, roteamento ou dataset de referência.
