"""Workflow de uso unico da carga da vistoria (segredos PRAZO_VIST_1..N -> VPS)."""
import sys, textwrap

script, saida, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
codigo = textwrap.indent(open(script, encoding="utf-8").read(), " " * 12)
envs = "\n".join(f"          P{i}: ${{{{ secrets.PRAZO_VIST_{i} }}}}" for i in range(1, n + 1))
junta = "".join(f'"$P{i}"' for i in range(1, n + 1))
yaml = f"""# USO UNICO: carga da vistoria do prazo de entrega (15/10/2026) no banco do rastreio: prazo registrado do TMS por pedido,
# prazo proprio por cliente+CEP e bloqueios por cliente/regiao. A carga vem de segredos temporarios (o repositorio e publico;
# ela nunca vai para o codigo nem para o log). Sem "CARREGAR" so relata. Backup do banco antes de gravar.
# Apagar este arquivo e os segredos PRAZO_VIST_1..{n} depois do uso.
name: "Uso unico - Carga da vistoria do prazo"

on:
  workflow_dispatch:
    inputs:
      confirmar:
        description: "Vazio = so relata. Digite CARREGAR para gravar (com backup do banco antes)"
        required: false
        default: ""
        type: string

concurrency:
  group: rastreamento-production-deploy
  cancel-in-progress: false

jobs:
  carga:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Montar a carga a partir dos segredos
        env:
{envs}
        run: |
          set -euo pipefail
          mkdir -p carga
          printf '%s' {junta} | base64 -d > carga/vistoria.txt.gz
          gzip -t carga/vistoria.txt.gz
          echo "linhas: $(gzip -dc carga/vistoria.txt.gz | wc -l) | sha256: $(gzip -dc carga/vistoria.txt.gz | sha256sum | cut -c1-16)"

      - name: Enviar a carga para a VPS
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{{{ secrets.VPS_HOST }}}}
          username: ${{{{ secrets.VPS_USER }}}}
          key: ${{{{ secrets.VPS_SSH_KEY }}}}
          port: 22
          source: carga/vistoria.txt.gz
          target: /tmp/prazo-vistoria
          strip_components: 1

      - name: Relatar / gravar na VPS
        uses: appleboy/ssh-action@v1.0.3
        env:
          CONFIRMAR: ${{{{ inputs.confirmar }}}}
        with:
          host: ${{{{ secrets.VPS_HOST }}}}
          username: ${{{{ secrets.VPS_USER }}}}
          key: ${{{{ secrets.VPS_SSH_KEY }}}}
          port: 22
          envs: CONFIRMAR
          command_timeout: 10m
          script: |
            set -euo pipefail
            CONFIRMAR="$CONFIRMAR" python3 - <<'PY'
{codigo}            PY
"""
open(saida, "w", encoding="utf-8", newline="\n").write(yaml)
print("ok", len(yaml))
