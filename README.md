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
| **PinBank** | Roxo e branco | https://rastreamento.agylog.com.br/tracking/pinbank/ |
| **Inter** | Laranja e branco | https://rastreamento.agylog.com.br/tracking/inter/ |

---

## Empresas parceiras

Este sistema foi desenvolvido em colaboração direta com as seguintes instituições:

| Empresa | Segmento |
| --- | --- |
| **Tribanco / Tricard** | Banco e cartão de crédito |
| **BRB — Banco de Brasília** | Banco público do DF |
| **BRB DUX** | Fintech do grupo BRB |
| **Panini** | Editora e distribuidora |
| **PinBank** | Fintech / Banco digital |
| **Inter** | Banco digital |

---

## Stack

`HTML · CSS · JavaScript · Python · Flask · nginx · Linux VPS`

**Custo de infraestrutura: R$ 0,00**

---

## Como funciona

```
URL: /tracking/{slug}/
           ↓
  Resolve tenant pelo slug
           ↓
  Carrega tema visual (logo, cores, header)
           ↓
  Consulta status no TMS da AgyLog
           ↓
  Renderiza página com identidade do cliente
```

O fluxo de desenvolvimento e os temas por cliente foram criados com auxílio de fluxo de trabalho assistido por IA (Claude Code), acelerando a entrega de cada nova identidade visual.
