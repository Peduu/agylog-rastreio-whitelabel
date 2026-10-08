import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import KITS, rota_pecas, scenes_for  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def emit(client):
    cenas = scenes_for(client)
    destino = os.path.join(ROOT, "static", "scenes", f"{client}.js")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write("/* GERADO por tools/scenes/build.py - nao editar a mao */\n")
        f.write("window.AgyScenes = window.AgyScenes || {};\n")
        f.write(f"window.AgyScenes.{client} = {json.dumps(cenas, ensure_ascii=False)};\n")
    return destino, os.path.getsize(destino), len(cenas)


def emit_rota(client):
    """Pecas da cena de rota do cartao "Onde esta seu pedido" (o navegador monta; ver static/localizacao.js)."""
    destino = os.path.join(ROOT, "static", "scenes", f"{client}-rota.js")
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write("/* GERADO por tools/scenes/build.py - nao editar a mao (pecas da cena de rota do cartao de localizacao) */\n")
        f.write("window.AgyRotas = window.AgyRotas || {};\n")
        f.write(f"window.AgyRotas.{client} = {json.dumps(rota_pecas(client), ensure_ascii=False)};\n")
    return destino, os.path.getsize(destino)


if __name__ == "__main__":
    for c in (sys.argv[1:] or list(KITS)):
        print(*emit(c))
        print(*emit_rota(c))
