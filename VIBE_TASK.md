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
