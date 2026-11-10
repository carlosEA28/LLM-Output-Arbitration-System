# Design

## Context

`src/nodes/critics.py` já possui `_failure_category`, `MAX_LLM_ATTEMPTS = 2` e `_invoke_with_retries`; cada crítico devolve apenas `failed_critics` quando falha. Testes atuais cobrem `google.genai.errors.ClientError(429/401)`, `GoogleRateLimitError` com causa, timeout e falha persistente. Na versão instalada de `langchain-google-genai`, `GoogleRateLimitError` e `GoogleAPIError` são tipos distintos; o cliente expõe `max_retries` com padrão 6 e ignora extras, de modo que `retries=1` no Logic Critic não limita tentativas internas. O grafo agrega listas de críticas/falhas e o veredito já é `inconclusive` quando falta dimensão ou há crítico falho. A SPEC-01 usa `evaluation_pass: null` para execução parcial.

O runner já tem `--limit` e `--output`, mas não seleção por ID, intervalo ou proteção contra sobrescrita. O diretório padrão contém relatórios anteriores. Ver proposta e specs deste change.

## Goals / Non-Goals

**Goals:**

- Tornar a contagem de chamadas ao modelo previsível e verificável em testes, inclusive no cliente Google.
- Levar metadados seguros do crítico até o JSON e Markdown sem perder críticas válidas de outras dimensões.
- Permitir reexecução seletiva em saída nova e recusar substituição implícita do baseline.

**Non-Goals:**

- Prometer eliminação de rate limits, respeitar dinamicamente todos os cabeçalhos de quota ou introduzir fila.
- Alterar scoring, prompts, adjudicação ou o desenho de nós/arestas do grafo.

## Decisions

### Classificação por tipo e código

Priorizar tipos específicos do wrapper Google (como `GoogleRateLimitError`) antes de `ChatGoogleGenerativeAIError`; quando houver `__cause__` tipado como `google.genai.errors.APIError`, usar seu `code`. Para `GoogleAPIError`, usar o código e só considerar 5xx transitório. Mapear timeout e conexão tipados; 401/403, 400/404 e configuração inválida terminam sem retry. Erros genéricos ficam `call_error` e não são repetidos. Não fazer busca textual em `str(exc)`, pois mensagens podem conter tokens ou payloads.

Alternativa considerada: todo `GoogleAPIError` como transitório. O nome da classe não determina se a resposta é 5xx ou um erro permanente.

### Um único orçamento de tentativas

Manter `_invoke_with_retries` como único ponto de retry: no máximo duas invocações e uma espera de backoff exponencial limitada (base 1 s, teto 2 s neste orçamento). Configurar `ChatGoogleGenerativeAI(max_retries=1)`, que na versão instalada corresponde a uma tentativa interna; manter `ChatOpenAI(max_retries=0)`. Testar a configuração do objeto real/argumentos para impedir regressão por parâmetro ignorado. Retornar a contagem efetiva para o diagnóstico; construção do cliente pode falhar antes de invocar o modelo e gera `attempts: 0`.

Alternativa considerada: deixar retry SDK e retry externo ativos. O produto do número de tentativas deixa o limite obscuro e pode agravar quotas.

### Metadados de cada crítico no estado

Adicionar `critic_diagnostics` como lista agregada no `ArbitrationState`, com um registro por crítico: `dimension`, `provider`, `attempts`, `status` (`success`/`failed`) e `category` (`null` no sucesso). Os nós continuam retornando `critiques` ou `failed_critics`; o novo campo é aditivo. `_record_failure` e logs usam valores de enumeração/controlados e nunca `str(exc)`. O runner da SPEC-01 copia somente esses campos permitidos, inclui-os em `results.json` e os apresenta no Markdown dos casos inconclusivos. Ausência do novo campo em estados antigos resulta em lista vazia, mantendo compatibilidade.

Alternativa considerada: correlacionar logs externos para deduzir categoria. Isso não entrega um relatório autocontido e perde a relação confiável entre caso e crítico.

### Seleção, carga e saída protegida

Adicionar `--case-id` repetível, aplicado antes de `--limit`, preservando a ordem do dataset e rejeitando IDs desconhecidos. `--interval-seconds` aceita número finito não negativo e dorme somente entre casos executados; padrão zero. Manter `--output` e o diretório padrão, mas verificar `results.json` e `summary.md` antes de construir/invocar o grafo: se algum existir, recusar a execução, salvo `--overwrite` explícito. Documentar exemplos de reexecução em um novo diretório. A opção de sobrescrita é intencionalmente clara e funciona para migração dos comandos antigos.

Alternativa considerada: criar saída com timestamp por padrão. Isso evita colisões, mas muda o caminho padrão consumido por scripts existentes e dificulta localizar o relatório sem outro mecanismo.

## Risks / Trade-offs

- [Versões futuras do cliente podem mudar semântica de `max_retries`] → teste de contrato para a versão instalada e revisão ao atualizar dependências.
- [Categoria interna não cobre exceções não tipadas] → classificá-las como `call_error`, sem retry; não inferir por mensagem.
- [Um retry pode não bastar sob quota prolongada] → reportar falha operacional e permitir reexecução seletiva; não aumentar silenciosamente o orçamento.
- [Proteção de saída muda scripts que dependem de sobrescrita] → mensagem de erro com `--output`/`--overwrite` e documentação atualizada.
- [Estado antigo sem `critic_diagnostics`] → runner mantém lista vazia e usa `failed_critics` como diagnóstico mínimo da SPEC-01.

## Migration Plan

Atualizar código, testes offline e README em conjunto. Validar regressão dos testes de críticos, grafo e avaliação; executar reexecuções reais apenas em diretório novo. Para rotinas que substituem relatórios intencionalmente, acrescentar `--overwrite`. Reverter o commit restaura a política e a CLI anteriores; relatórios já gerados permanecem legíveis pelos campos existentes.
