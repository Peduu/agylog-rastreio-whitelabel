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

Nunca versionar valores reais de `.env`, `SECRET_KEY`, `TMS_API_TOKEN`, banco SQLite, backups ou importações operacionais.
