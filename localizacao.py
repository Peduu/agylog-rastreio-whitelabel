"""Localizacao publica do pedido: cidades das unidades AGYLOG pelo historico do TMS (spec de 08/10/2026).

Regras que nao podem regredir:
- so cidade/UF da unidade; NUNCA latitude/longitude do TMS (na entrega podem revelar o endereco do destinatario);
- a coordenada desenhada e a da sede do municipio no IBGE, casada SO por nome normalizado + UF (nunca por aproximacao):
  sem casamento, a cidade aparece no texto mas nao vira ponto no mapa;
- CCXP: nada de devolucao nem remetente;
- texto SIMPLES (Pedro, 09/10/2026): uma linha com a rota e seta ("Sao Paulo/SP -> Curitiba/PR"), sem frase longa;
  detalhes (datas, destino) ficam no trilho embaixo do mapa.
"""
import json
import os
import re
import unicodedata
from datetime import datetime

CAMINHO_MUNICIPIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "municipios.json")
APELIDOS = {}   # (UF, nome normalizado como o TMS escreve) -> nome normalizado do IBGE; so grafias confirmadas
_MUNICIPIOS = None

STATUS_COM_LOCAL = {"preparacao_transporte", "transferencia_franquia", "chegada_franquia", "em_rota_entrega",
                    "atencao", "devolucao", "devolvido", "entregue"}
DESTINO_CONHECIDO = {"chegada_franquia", "em_rota_entrega", "atencao", "entregue"}
PROBLEMA = {"atencao", "devolucao", "devolvido"}


def normalizar(texto):
    t = unicodedata.normalize("NFKD", str(texto or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).upper()
    return re.sub(r"[^A-Z0-9]+", " ", t).strip()


def carregar_municipios(caminho=CAMINHO_MUNICIPIOS):
    with open(caminho, encoding="utf-8") as f:
        return {(uf, normalizar(nome)): (nome, lat, lon) for uf, nome, lat, lon, _cap in json.load(f)}


def _municipios():
    global _MUNICIPIOS
    if _MUNICIPIOS is None:
        _MUNICIPIOS = carregar_municipios()
    return _MUNICIPIOS


def localizar_cidade(cidade, uf):
    """{cidade, uf, lat, lon} com o nome OFICIAL do IBGE, ou None. Nunca aproxima."""
    uf = str(uf or "").strip().upper()
    nome = normalizar(cidade)
    if not nome or not re.fullmatch(r"[A-Z]{2}", uf):
        return None
    achado = _municipios().get((uf, APELIDOS.get((uf, nome), nome)))
    if not achado:
        return None
    oficial, lat, lon = achado
    return {"cidade": oficial, "uf": uf, "lat": lat, "lon": lon}


def _data(texto):
    t = str(texto or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(t[:19], fmt)
        except ValueError:
            pass
    return None


def ocorrencias_com_local(lista):
    """Ocorrencias do TMS -> [{data, unidade, cidade, uf}] em ordem de data; so as que tem cidade, UF e data validas.
    Nao copia latitude/longitude."""
    saida = []
    for item in lista or []:
        cidade = str(item.get("nomeCidade") or "").strip()
        uf = str(item.get("uf") or "").strip().upper()
        quando = _data(item.get("dtOcorrencia"))
        if cidade and uf and quando:
            saida.append({"data": quando.strftime("%Y-%m-%d %H:%M:%S"), "unidade": str(item.get("unidadeOcorrencia") or "").strip(),
                          "cidade": cidade, "uf": uf})
    saida.sort(key=lambda o: o["data"])
    return saida


def _curta(data_iso):
    d = _data(data_iso)
    return d.strftime("%d/%m %H:%M") if d else ""


def _paradas(ocorrencias):
    """Cidades distintas em ordem; a mesma cidade em seguida (duas unidades ou varias leituras) e uma parada so."""
    paradas = []
    for o in ocorrencias:
        uf = str(o.get("uf") or "").strip().upper()
        chave = (uf, normalizar(o.get("cidade")))
        if not chave[1] or not uf:
            continue
        if paradas and paradas[-1]["chave"] == chave:
            paradas[-1]["ultima"] = o["data"]
            continue
        ibge = localizar_cidade(o["cidade"], uf)
        nome = f'{ibge["cidade"]}/{uf}' if ibge else f'{str(o["cidade"]).strip().title()}/{uf}'
        paradas.append({"chave": chave, "nome": nome, "uf": uf, "ibge": ibge, "primeira": o["data"], "ultima": o["data"]})
    return paradas


def _item(slot, titulo, sub, icone=None):
    item = {"slot": slot, "titulo": titulo, "sub": sub}
    if icone:
        item["icone"] = icone
    return item


def _cidade(parada, atual=False):
    """Cidade da linha da rota; a ATUAL vai em destaque e leva a bandeira da UF."""
    return {"t": parada["nome"], "uf": parada["uf"], "atual": atual}


def montar_localizacao_publica(ocorrencias, status_key, cliente=""):
    """None ou {linha, transito, trilho, pontos, atualizado}.

    linha = cidades da rota para mostrar com seta entre elas (origem -> onde esta); transito = True quando o pedido
    saiu e ainda nao chegou em outra unidade (o front mostra "-> em transito" depois da cidade).
    """
    if status_key not in STATUS_COM_LOCAL:
        return None
    paradas = _paradas(ocorrencias or [])
    if not paradas:
        return None
    ccxp = str(cliente or "").strip().lower() == "ccxp"
    origem, atual = paradas[0], paradas[-1]
    um = len(paradas) == 1
    A = atual["nome"]
    agora = _curta(atual["ultima"])
    t_origem = _item(1, origem["nome"], f'saiu · {_curta(origem["ultima"])}')
    destino_ok = status_key in DESTINO_CONHECIDO and not (ccxp and status_key in PROBLEMA)
    linha = ([] if um else [_cidade(origem)]) + [_cidade(atual, True)]
    transito = False

    if status_key in PROBLEMA and (ccxp or status_key != "atencao"):
        trilho = ([] if um else [t_origem]) + [_item(2, A, f"agora · {agora}")]
    elif status_key == "preparacao_transporte":
        trilho = [_item(2, A, f'desde {_curta(atual["primeira"])}'), _item(3, "Destino", "a definir")]
    elif status_key == "transferencia_franquia" and um:
        transito = True
        trilho = [t_origem, _item(2, "Unidade de entrega", "a definir")]
    elif status_key == "transferencia_franquia":
        trilho = [t_origem, _item(2, A, f"agora · {agora}"), _item(3, "Unidade de entrega", "a definir")]
    else:
        textos = {
            "chegada_franquia": (f'chegou · {_curta(atual["primeira"])}', "próxima etapa"),
            "em_rota_entrega": ("unidade de entrega", f"em rota · {agora}"),
            "atencao": ("unidade de entrega", f"tentativa · {agora}"),
            "entregue": ("unidade de entrega", f"entregue · {agora}"),
        }
        sub2, sub3 = textos[status_key]
        trilho = ([] if um else [t_origem]) + [_item(2, A, sub2), _item(3, "Seu endereço", sub3, "chegada")]

    pontos = []
    if atual["ibge"]:
        com_ibge = [p for p in paradas if p["ibge"]]
        for i, p in enumerate(com_ibge):
            papel = "atual" if p is atual else ("origem" if i == 0 else "passagem")
            pontos.append({"papel": papel, "nome": p["nome"], "uf": p["uf"], "lat": p["ibge"]["lat"], "lon": p["ibge"]["lon"]})
        if destino_ok:
            pontos.append({"papel": "destino", "nome": atual["nome"], "uf": atual["uf"],
                           "lat": atual["ibge"]["lat"], "lon": atual["ibge"]["lon"]})
            if status_key == "entregue":
                pontos = [p for p in pontos if p["papel"] != "atual"]   # entregue: a bandeira xadrez substitui o pin
    return {"linha": linha, "transito": transito, "trilho": trilho, "pontos": pontos, "atualizado": agora}
