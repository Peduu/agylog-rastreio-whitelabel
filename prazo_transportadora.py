"""Previsao de entrega das transportadoras parceiras (Claude, 21/10/2026). Regra do Pedro: puxar o prazo de onde for possivel.

Ordem na pagina publica (cada fonte so vale com data de hoje em diante; vencida passa para a proxima):
1) Total Express: previsaoEntregaAtualizada, depois previsaoEntrega, da MESMA consulta do cartao dos Correios
   (buscar_codigo_correios_total). Em 21/10/2026 a Total devolvia os dois campos vazios para o CCXP: entra sozinho quando
   vierem preenchidos.
2) Logan (SimExpress): consumidor.PrevisaoEntrega, guardada pela rotina Logan->TMS da VPS (recuperacao por pedido) em
   /home/projetos/atualizar_logan/previsoes_logan.json. A pagina NAO consulta a Logan: ela limita consultas por pedido e a
   rotina que lanca os eventos no TMS precisa delas.
3) prazo registrado do TMS / tabela por CEP (prazo_cep.py).
O liga/desliga do prazo no admin vale para todas as fontes; o cliente so ve prazo com o pedido a caminho.

INTEGRACAO NOVA NO RASTREIO (transportadora, parceiro, API): ver se a resposta traz previsao/prazo e incluir aqui.
"""
import json
import os
import re
import threading
from datetime import date, datetime, timedelta
from pathlib import Path

LOGAN_PREVISOES_FILE = os.getenv("LOGAN_PREVISOES_FILE", "/home/projetos/atualizar_logan/previsoes_logan.json")
LOGAN_VALIDADE_DIAS = 3   # previsao que a rotina nao reviu nesse tempo nao vale (pedido saiu da lista ou a Logan travou)
_LOGAN = {"chave": None, "pedidos": {}}
_LOGAN_LOCK = threading.Lock()


def data_de(valor):
    """date de "AAAAMMDD", "AAAA-MM-DD[THH:MM:SS]" ou "DD/MM/AAAA[ HH:MM]"; None se vazio ou fora do formato."""
    texto = str(valor or "").strip()
    for fmt, tamanho in (("%Y%m%d", 8), ("%Y-%m-%d", 10), ("%d/%m/%Y", 10)):
        if len(texto) < tamanho:
            continue
        if fmt == "%Y%m%d" and not re.fullmatch(r"\d{8}", texto):
            continue
        try:
            return datetime.strptime(texto[:tamanho], fmt).date()
        except ValueError:
            continue
    return None


def previsao_total(payload, codigo):
    """Previsao da Total para o pedido (a atualizada primeiro), ou None."""
    codigo = str(codigo or "").strip().upper()
    if not isinstance(payload, dict) or not codigo:
        return None
    for encomenda in payload.get("data") or []:
        if not isinstance(encomenda, dict) or str(encomenda.get("pedido") or "").strip().upper() != codigo:
            continue
        for campo in ("previsaoEntregaAtualizada", "previsaoEntrega"):
            previsao = data_de(encomenda.get(campo))
            if previsao:
                return previsao
    return None


def _pedidos_logan(caminho):
    """Conteudo do arquivo da rotina, relido so quando ele muda. Sem arquivo ou ilegivel = nada."""
    try:
        estado = os.stat(caminho)
    except OSError:
        return {}
    chave = (str(caminho), estado.st_mtime_ns, estado.st_size)
    with _LOGAN_LOCK:
        if _LOGAN["chave"] == chave:
            return _LOGAN["pedidos"]
    try:
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        pedidos = dados.get("pedidos") if isinstance(dados, dict) else None
        pedidos = pedidos if isinstance(pedidos, dict) else {}
    except (OSError, ValueError):
        pedidos = {}
    with _LOGAN_LOCK:
        _LOGAN.update(chave=chave, pedidos=pedidos)
    return pedidos


def previsao_logan(codigos, caminho=None, hoje=None):
    """Previsao da Logan para o pedido (numero do pedido ou AR), ou None. Mais de uma data = nada."""
    pedidos = _pedidos_logan(caminho or LOGAN_PREVISOES_FILE)
    if not pedidos:
        return None
    limite = (hoje or date.today()) - timedelta(days=LOGAN_VALIDADE_DIAS)
    datas = set()
    for codigo in codigos or []:
        entrada = pedidos.get(str(codigo or "").strip().upper())
        if not isinstance(entrada, dict):
            continue
        visto = data_de(entrada.get("visto_em"))
        previsao = data_de(entrada.get("previsao"))
        if visto and previsao and visto >= limite:
            datas.add(previsao)
    return datas.pop() if len(datas) == 1 else None


def primeira_valida(previsoes, hoje):
    """Primeira previsao de hoje em diante (nunca vencida), na ordem recebida; None se nenhuma."""
    return next((p for p in previsoes if p and p >= hoje), None)
