# Códigos de demonstração AGY

Dados fictícios, sem gravação no banco e sem chamadas ao TMS. Os códigos exatos
AGY1 a AGY10 ficam reservados para demonstração em todos os temas.

| Código | Situação |
| --- | --- |
| AGY1 | Aguardando postagem |
| AGY2 | Em preparação |
| AGY3 | Em transferência |
| AGY4 | Na unidade final |
| AGY5 | Em rota de entrega |
| AGY6 | Insucesso / aguardando tratativa |
| AGY7 | Em devolução |
| AGY8 | Devolvido |
| AGY9 | Entregue |
| AGY10 | Reentrega / tratativa realizada |

Uso após publicação: `/tracking/caoa/AGY1`, `/tracking/ccxp/AGY1`, etc.
O mesmo código funciona no tema escolhido. Os antigos CAOA1 a CAOA4 permanecem
exclusivos do CAOA.

No CCXP, AGY6, AGY7 e AGY8 exibem **Insucesso na entrega**;
AGY10 exibe **Tratativa concluída**, com a etapa Reenvio. Não há textos de devolução no CCXP.
Nos demais temas AGY10 usa a apresentação existente de atenção/reentrega.

No Simple Company, informe **Demonstração AGY** como nome do destinatário.
A validação dos nomes dos pedidos reais permanece ativa.

Não use esses códigos em envios reais. As datas fictícias são relativas ao dia da consulta.

## Códigos ROTA1 a ROTA9 (cartão "Onde está seu pedido", 08/10/2026)

Mesmos status dos AGY1 a AGY9, com o cartão de localização (linha com a bandeira do estado, mapa com
pin e nome das cidades, bandeira quadriculada só quando o pedido foi entregue, trilho com as datas). Rota fictícia:
São Paulo/SP → Curitiba/PR → Londrina/PR. Funcionam em todos os temas: `/tracking/paranabanco/ROTA3`,
`/tracking/brb/ROTA5` etc.

Desde 15/10/2026 o cartão aparece para **todos** os pedidos (reais e AGY), cada cliente com as suas cores.
Para voltar a mostrar só nos ROTA: `PUBLIC_TRACKING_LOCALIZACAO=demo` no `/etc/rastreamento.env` e reiniciar o serviço. Spec e plano: `SPEC-localizacao-rastreio-2026-10-08.md`
e `PLANO-localizacao-rastreio-2026-10-08.md` (pasta `instruções API` do Pedro).
