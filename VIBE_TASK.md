# Demonstrações genéricas de rastreamento

Objetivo: um código AGY por estado visual, em todos os portais.

- [x] Inspecionar rotas, estados e demonstrações existentes.
- [x] Implementar AGY1 a AGY10 com dados fictícios.
- [x] Reutilizar as regras exclusivas do CCXP.
- [x] Suportar o fluxo de nome do Simple Company.
- [x] Validar demos, isolamento dos pedidos reais e regressões (21 testes; pacote de deploy validado).
- [x] Publicar em produção (GitHub Actions 36142462937, commit b86aa4e).
- [x] Verificar produção: 17 consultas de demonstração e 3 páginas HTTP 200.

Aceite: códigos exatos funcionam por tema; nenhum dado real é consultado nas demos;
CCXP não exibe devolução; códigos fora da lista seguem a consulta normal.

Arquivos principais: app.py, tests/test_demo_agy.py, DEMO-AGY.md.

Deploy: https://github.com/Peduu/agylog-rastreio-whitelabel/actions/runs/36142462937
Resultado: todos os códigos validados no CAOA; regras CCXP validadas em AGY6/7/8/10;
amostras Panini, IP2W e Simple Company confirmadas. Sem bloqueios pendentes nesta tarefa.

## Integração automática Total → Correios (em investigação)

Objetivo: obter automaticamente o código postal por pedido e disponibilizar o
botão em todos os clientes, preservando associação correta entre remessas.

- [x] Conferir implementação e versão publicada do cadastro manual.
- [x] Consultar, somente leitura na VPS, os dois exemplos informados pelo usuário.
- [x] Confirmar: API TMS atual não retorna código postal em nenhum exemplo;
  Interlog retorna found=false em ambos; apenas o primeiro possui vínculo manual.
- [x] Tentar pesquisa do segundo exemplo no Total Conecta.
- [x] Localizar campo na tela: Dados operacionais > Número redespacho; pedido
  identificado pelo campo Encomenda/Id. do cliente nos Dados fiscais.
- [x] Confirmar Relatórios > Busca por lote, modalidade Pedido, limite de 25000 itens.
- [x] Solicitar relatório de teste dos dois exemplos fornecidos pelo usuário.
- [x] Inspecionar colunas do arquivo exportado: `Pedido` contem OMLTCO e
  `Redespacho` contem o codigo postal; dois exemplos conferidos sem conflito.
- [x] Confirmar fonte automática suportada: API oficial de Status de Entrega.
- [x] Testar a API oficial de Status de Entrega com dois pedidos reais: ambos
  retornaram `REDESPACHADO CORREIO - AD...BR` em `tracking[].descricao`.
- [x] Adaptar o admin para importar diretamente o CSV Busca por lote da Total,
  preservando a entrada manual e bloqueando vinculos ambiguos.
- [x] Incluir o vinculo postal no endpoint exclusivo da Simple Company; os
  demais clientes ja usam o fluxo publico compartilhado.
- [x] Eliminar a exportação recorrente: consultar a API por pedido na abertura
  do rastreio e usar cache (30 min com código; 5 min sem código).
- [x] Implementar consulta direta por pedido na API oficial, com validação do
  pedido retornado, detecção de conflito, cache e fallback para vínculo manual.
- [x] Validar o importador de ponta a ponta com o CSV real em banco temporario;
  2 de 2 vinculos gravados, sem conflitos; suite completa com 30 testes aprovada.
- [x] Validar a resposta real dos dois pedidos, a suite local (33 testes) e o
  manifesto de deploy.
- [x] Pedro autorizou ativar a integração na VPS com backup, configuração
  das duas variáveis no serviço, publicação e validação.
- [x] Segredos da Total cadastrados no GitHub Actions sem valores no Git.
- [ ] Publicar o código com backup e rollback do código e do ambiente.
- [ ] Validar os dois exemplos no portal público após publicação.

Login restabelecido pelo usuário. O segundo exemplo foi localizado na Total,
com Número redespacho preenchido e evento Disponível para retirada.
O relatorio real foi fornecido pelo usuario e contem os dois vinculos esperados.
A API oficial foi comprovada com autenticação direta; os dois pedidos de exemplo
retornaram o mesmo código dos Correios já visto no relatório. O serviço precisa
receber `TOTAL_EXPRESS_API_USER` e `TOTAL_EXPRESS_API_PASSWORD` por ambiente na
VPS antes da publicação. Nenhuma alteração em produção foi feita nesta etapa.
Não reinterpretar ENTREGUE como envio aos Correios sem comprovar a semântica do evento.
