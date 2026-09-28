# Deploy do rastreamento

Deploy manual preparado a partir do padrão validado do `mqf-agylog-adm`.

Fluxo previsto:

1. Disparo manual pelo GitHub Actions com confirmação `DEPLOY`.
2. Validação local do manifesto.
3. Empacotamento somente dos arquivos listados em `deploy/deploy-manifest.tsv`.
4. Envio do pacote para a VPS por SSH/SCP.
5. Backup dos arquivos atuais antes de qualquer sobrescrita.
6. Aplicação restrita a `/home/rastreamento/`.
7. Reinstalação de dependências, restart de `rastreamento.service` e smoke test público.
8. Rollback automático se qualquer etapa falhar.

Secrets esperados no repositório:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `TOTAL_EXPRESS_API_USER`
- `TOTAL_EXPRESS_API_PASSWORD`

Nunca versionar valores reais de `.env`, `SECRET_KEY`, `TMS_API_TOKEN`, banco SQLite, backups ou importações operacionais.

## Integração Total Express → Correios

O portal consulta a API oficial de Status de Entrega pelo número do pedido.
Quando um evento `REDESPACHADO CORREIO` contém um código postal, o botão dos
Correios aparece nos portais que compartilham o endpoint público. O vínculo
manual continua disponível se a API falhar ou não retornar o código.

O workflow recebe `TOTAL_EXPRESS_API_USER` e `TOTAL_EXPRESS_API_PASSWORD`
como segredos do GitHub Actions, faz backup e atualiza `/etc/rastreamento.env`
(permissão 600, root) por SSH, sem incluir valores no Git ou no pacote.
Confirmar os dois pedidos de referência no endpoint
`/api/rastrear`, incluindo o código dos Correios em `rastreioTerceiro`.
