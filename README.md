# AgyLog · Rastreio White-Label (Multi-Tenant)

Portal de rastreamento de encomendas **white-label** em produção: uma única base de código atende vários clientes, cada um com **identidade visual própria** (logotipo, cores e header co-branded) resolvida dinamicamente pelo *slug* na URL.

> **Meu papel no projeto:** front-end **100% meu** (HTML, CSS, JavaScript e toda a identidade visual por cliente) e **participação no desenvolvimento do back-end** (rotas, integração e publicação).

---

## Demonstrações ao vivo

Mesmo sistema, tema próprio para cada cliente — todos co-branded com a AgyLog (AGY):

| Cliente | Identidade visual | Link |
| --- | --- | --- |
| **Tribanco · Tricard** | Teal sobre azul | https://rastreamento.agylog.com.br/tracking/tricard/ |
| **BRB DUX** | Preto e branco | https://rastreamento.agylog.com.br/tracking/BRBDUX/ |
| **BRB Card** | Azul institucional | https://rastreamento.agylog.com.br/tracking/BRB/ |
| **Panini** | Amarelo, vermelho e preto | https://rastreamento.agylog.com.br/tracking/panini/ |

> As páginas abrem na tela de consulta. A tela de status completa (situação atual, etapas e histórico) é exibida ao informar um código de rastreio válido.

---

## Destaques

- **Multi-tenant por slug** — `/tracking/<cliente>/` carrega logo, paleta e header específicos sem duplicar a base de código.
- **Co-branding automático** — lockup do cliente + AgyLog no header, com proporção e espaçamento consistentes.
- **Consulta por código** — campo de busca com colar rápido e validação de entrada.
- **Tela de status** — destaque com a situação atual, etapas, linha do tempo e histórico de movimentações.
- **Responsivo** — header e cards adaptados para desktop e mobile.
- **Operação enxuta** — em produção em VPS própria, com HTTPS gratuito e custo de operação próximo de zero.

---

## Stack

`HTML` · `CSS` · `JavaScript` · `Python` · `Flask` · `Gunicorn` · `nginx` · `VPS Linux` · `Let's Encrypt`

---

## Como funciona

1. O usuário acessa `/tracking/<slug>/` (ex.: `tricard`, `BRBDUX`, `BRB`, `panini`).
2. O back-end identifica o cliente pelo slug e aplica o tema correspondente (logo, cores e header co-branded).
3. O usuário informa o código de rastreio e acompanha a entrega em uma tela de status padronizada.

---

_Projeto em produção, operado pela AgyLog / CorelliLog._
