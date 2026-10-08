"""Prepara os dados geograficos do cartao "Onde esta seu pedido" (rodar so quando a fonte mudar).

Uso:
  python tools/geo/preparar_geo.py <municipios.csv do kelvins> <malha das UFs do IBGE (geojson)>
  malha: https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&intrarregiao=UF&qualidade=intermediaria

Gera:
  data/municipios.json         [[uf, nome, lat, lon, capital], ...]  sede de cada municipio (IBGE); usado pelo backend.
                               JSON e nao CSV porque o .gitignore barra *.csv no repositorio publico.
  static/data/uf/<UF>.json     [[[lon, lat], ...], ...]  contorno de cada UF (malha oficial do IBGE, qualidade intermediaria)
  static/data/uf/indice.json   {"PR": [lon_min, lat_min, lon_max, lat_max], ...}  o mapinha so baixa as UFs que aparecem
"""
import csv
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UF_POR_CODIGO = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
    "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS",
    "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}


def municipios(origem, destino):
    linhas = []
    with open(origem, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            linhas.append([UF_POR_CODIGO[r["codigo_uf"]], r["nome"].strip(), round(float(r["latitude"]), 5),
                           round(float(r["longitude"]), 5), int(r["capital"])])
    linhas.sort(key=lambda x: (x[0], x[1]))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join(json.dumps(l, ensure_ascii=False) for l in linhas) + "\n]\n")
    return len(linhas)


def contornos(origem, pasta):
    with open(origem, encoding="utf-8") as f:
        geo = json.load(f)
    os.makedirs(pasta, exist_ok=True)
    indice = {}
    for feat in geo["features"]:
        uf = UF_POR_CODIGO[str(feat["properties"]["codarea"])]
        g = feat["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        aneis = [[[round(lon, 3), round(lat, 3)] for lon, lat in poly[0]] for poly in polys]   # anel externo de cada parte
        lons = [lon for anel in aneis for lon, _ in anel]
        lats = [lat for anel in aneis for _, lat in anel]
        indice[uf] = [min(lons), min(lats), max(lons), max(lats)]
        with open(os.path.join(pasta, f"{uf}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(aneis, f, separators=(",", ":"))
    with open(os.path.join(pasta, "indice.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(indice, f, separators=(",", ":"), sort_keys=True)
    return len(indice)


if __name__ == "__main__":
    n = municipios(sys.argv[1], os.path.join(RAIZ, "data", "municipios.json"))
    u = contornos(sys.argv[2], os.path.join(RAIZ, "static", "data", "uf"))
    print(f"{n} municipios, {u} UFs")
