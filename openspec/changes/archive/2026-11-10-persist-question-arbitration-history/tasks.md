# Tasks

## 1. Armazenamento SQLite

- [x] 1.1 Criar o módulo específico de histórico com tabela, UUID, data UTC, transições de status e configuração `ARBITRATION_DB_PATH`; verificar com testes temporários que escrita e leitura persistem entre conexões e que valores opcionais são preservados.
- [x] 1.2 Ignorar o arquivo SQLite padrão no Git e verificar com `git check-ignore arbitrations.sqlite3`.

## 2. Ciclo de vida da geração

- [x] 2.1 Integrar o histórico ao serviço de geração e avaliação sem alterar `run_agents_graph()`; verificar por testes com geração e grafo simulados que o registro passa de `pending` a `completed`, mantém a resposta e o resultado validado e aceita veredito `inconclusive`.
- [x] 2.2 Registrar `failed` ou `timed_out` em falhas de geração, avaliação e veredito inválido, sem persistir detalhes da exceção; verificar por testes offline os status, a resposta gerada quando disponível e a ausência de payloads internos.

## 3. Contratos HTTP e documentação

- [x] 3.1 Acrescentar o ID ao sucesso de `POST /generate-and-evaluate` e `X-Arbitration-ID` ao sucesso e às falhas após criação do registro, preservando corpos de erro; atualizar testes de API e verificar ID consultável, HTTP 500/504 e ausência de registro para HTTP 422 e `POST /evaluate`.
- [x] 3.2 Implementar `GET /v1/arbitrations/{id}` com schema de transporte e respostas HTTP 200/404/422; verificar em testes de API registros completos, inconclusivos, com falha e leitura por outro cliente usando o mesmo arquivo SQLite.
- [x] 3.3 Documentar no README o fluxo de criação/consulta, status, cabeçalho de falha e configuração do caminho SQLite; verificar que exemplos e nomes de campos correspondem aos schemas e às rotas.

## 4. Verificação integrada

- [x] 4.1 Executar os testes direcionados de histórico e as regressões existentes de geração, avaliação direta, serviço e health; registrar resultados reais e verificar que importar a aplicação e consultar `/health` não cria o arquivo SQLite.
