# Design

## Context

Veja `proposal.md` para a motivação. Hoje `src/api/routes/arbitration.py` tem rotas síncronas para `/evaluate` e `/generate-and-evaluate`; `src/api/services/arbitration_service.py` já encapsula geração e `run_agents_graph()`. A resposta de geração usa `GenerationEvaluationResponse`, e erros HTTP 500/504 têm corpos genéricos. Não há banco de dados nem dependência de ORM.

## Goals / Non-Goals

**Goals:** Manter o trabalho síncrono fora do event loop, garantir que respostas HTTP 200 tenham um registro recuperável e que falhas após a criação do registro tenham status consultável. Preservar os contratos de domínio e a privacidade dos erros.

**Non-Goals:** Recuperação ou retomada de processos interrompidos, paginação/listagem, limpeza automática, busca, autenticação e persistência de `/evaluate`.

## Decisions

1. **Armazenamento:** usar `sqlite3` da biblioteca padrão em um módulo pequeno sob `src/api/`, com uma tabela específica para execuções. Colunas: `id` (UUID v4 em texto), `created_at` (UTC em ISO 8601), `status`, `original_question`, `generated_output` anulável e `evaluation_json` anulável. Serializar o resultado de `EvaluationResponse` em JSON para preservar os dados tipados já expostos pela API. Abrir uma conexão curta por operação e fechar antes das chamadas aos modelos, evitando manter transações abertas durante a avaliação. O arquivo padrão será `arbitrations.sqlite3` no diretório de execução, configurável por `ARBITRATION_DB_PATH`; ignorar esse arquivo no Git. Alternativas como ORM ou PostgreSQL acrescentam dependências e estrutura sem necessidade nesta etapa.
2. **Ciclo de vida:** depois da validação de entrada, inserir `pending` antes da geração. Após a geração, atualizar `generated_output` imediatamente. Após validar o resultado estruturado, atualizar `evaluation_json` e `status=completed` antes de responder HTTP 200. Em timeout propagado, marcar `timed_out`; nas demais falhas de geração/avaliação, marcar `failed`. Um veredito `inconclusive` válido continua sendo uma execução `completed`. O serviço da API coordena essas etapas usando as funções de geração e avaliação existentes; o grafo e seus schemas ficam intactos. Persistir apenas o resultado validado evita que um veredito inválido apareça no histórico como conclusão.
3. **Identificação e leitura:** incluir `id` no corpo de sucesso e `X-Arbitration-ID` nos cabeçalhos de sucesso e de erro após a inserção. Manter os corpos genéricos de HTTP 500/504; nunca gravar `str(exception)` ou payloads do provedor. `GET /v1/arbitrations/{id}` aceita UUID, retorna HTTP 404 para UUID ausente e um schema de transporte com metadados, resposta opcional e `evaluation` opcional. Um registro `pending` pode ser lido enquanto a execução está em curso. A consulta apenas abre o arquivo e a tabela quando necessário; importar a aplicação ou chamar `/health` não cria banco nem inicializa provedores.
4. **Falha de armazenamento:** uma falha ao inserir ou atualizar dados impede resposta de sucesso e retorna erro genérico HTTP 500. O ID só é anunciado quando o registro inicial existe. Se uma gravação de status falhar, a API não promete que a última transição foi persistida. Essa escolha evita informar ao cliente que uma avaliação foi salva quando não foi.

## Risks / Trade-offs

- [Interrupção abrupta pode deixar `pending`] → Expor o status real; retomada e reconciliação ficam fora deste escopo.
- [SQLite permite um escritor por vez] → Transações curtas e conexões por operação; volume e concorrência maiores podem exigir outra tecnologia futuramente.
- [Banco local contém perguntas e respostas potencialmente sensíveis] → Arquivo ignorado no Git, caminho configurável e nenhum detalhe de exceção armazenado. A API atual não possui autenticação; a consulta por ID segue o mesmo modelo de acesso público.
- [Mudança aditiva no corpo de sucesso] → Preservar todos os campos e valores atuais; atualizar os testes que verificam o conjunto exato de campos.

## Migration Plan

Criar a tabela automaticamente no primeiro acesso ao armazenamento; não há dados anteriores a migrar. Em implantação, usar um caminho persistente e gravável em `ARBITRATION_DB_PATH`. Reverter o código deixa o arquivo SQLite intacto; a versão anterior simplesmente não o utiliza.
