import os
import re
from datetime import datetime, timedelta

import requests


TMS_API_URL = os.getenv(
    "TMS_API_URL",
    "https://corellilog.tmselite.com/api/ocorrencias/ocorrencianotafiscaldepara",
)
TMS_API_TOKEN = os.getenv("TMS_API_TOKEN", "").strip()
TMS_API_TIMEOUT = int(os.getenv("TMS_API_TIMEOUT", "20"))
TMS_API_DEBUG = os.getenv("TMS_API_DEBUG", "").strip() == "1"


DE_PARA_OCORRENCIAS = {
    "1": {"statusBadge": "CRIADA", "ultimoStatus": "Criacao da solicitacao"},
    "2": {"statusBadge": "EM ROTA", "ultimoStatus": "Solicitacao em Rota"},
    "3": {"statusBadge": "AGENDADO", "ultimoStatus": "Agendamento da Solicitacao"},
    "5": {"statusBadge": "NAO COLETADO", "ultimoStatus": "Nao Coletado"},
    "6": {"statusBadge": "COLETADO", "ultimoStatus": "Coleta realizada"},
    "7": {"statusBadge": "CANCELADA", "ultimoStatus": "Cancelamento de solicitacao"},
    "10": {"statusBadge": "DEVOLVIDO", "ultimoStatus": "Devolucao Realizada"},
    "11": {"statusBadge": "NAO DEVOLVIDO", "ultimoStatus": "Nao Devolvido"},
    "13": {"statusBadge": "DEVOLUCAO EM ROTA", "ultimoStatus": "Geracao de lista de devolucao"},
    "14": {"statusBadge": "EM TRANSFERENCIA DEVOLUCAO", "ultimoStatus": "Envio de Transferencia para devolucao"},
    "15": {"statusBadge": "SEM MUDANCA DE STATUS", "ultimoStatus": "Cancelamento romaneio de coleta"},
    "16": {"statusBadge": "REAGENDADO", "ultimoStatus": "Reagendamento da Solicitacao"},
    "17": {"statusBadge": "TRANSFERENCIA ENTREGA RECEBIDA", "ultimoStatus": "Recebimento de transferencia entre unidades"},
    "19": {"statusBadge": "SEM MUDANCA DE STATUS", "ultimoStatus": "Alteracao de Status"},
    "20": {"statusBadge": "SEM MUDANCA DE STATUS", "ultimoStatus": "Cancelamento Lista de Transferencia"},
    "21": {"statusBadge": "AGENDADO", "ultimoStatus": "Tentativa de Agendamento"},
    "22": {"statusBadge": "SEM MUDANCA DE STATUS", "ultimoStatus": "Cancelamento romaneio de devolucao"},
    "23": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Pendencia de devolucao resolvida"},
    "24": {"statusBadge": "ARQUIVO RECEBIDO", "ultimoStatus": "Arquivo Recebido"},
    "25": {"statusBadge": "RECEBIDO", "ultimoStatus": "Coletado e recebido na base"},
    "27": {"statusBadge": "PENDENTE", "ultimoStatus": "Tratamento de Pendencia"},
    "28": {"statusBadge": "RECEBIDO", "ultimoStatus": "Recebimento de volumes para entrega"},
    "29": {"statusBadge": "ARMAZENADO", "ultimoStatus": "Volumes armazenados"},
    "30": {"statusBadge": "PROCESSADO", "ultimoStatus": "Picking realizado"},
    "31": {"statusBadge": "ENTREGUE", "ultimoStatus": "Entrega Realizada"},
    "32": {"statusBadge": "PENDENTE", "ultimoStatus": "Entrega nao Realizada"},
    "33": {"statusBadge": "REJEITADO", "ultimoStatus": "Remessa rejeitada na criacao"},
    "34": {"statusBadge": "SEM MUDANCA DE STATUS", "ultimoStatus": "Cancelamento de romaneio de entrega"},
    "35": {"statusBadge": "EM TRANSFERENCIA ENTREGA", "ultimoStatus": "Transferencia de volumes para entrega"},
    "36": {"statusBadge": "CUSTODIA", "ultimoStatus": "Tratamento de Pendencia (Devolver)"},
    "37": {"statusBadge": "CUSTODIA", "ultimoStatus": "Tratamento de Pendencia (Reentregar)"},
    "39": {"statusBadge": "INDENIZACAO", "ultimoStatus": "Baixa em indenizacao"},
    "40": {"statusBadge": "AGENDADO", "ultimoStatus": "Solicitacao removida do romaneio"},
    "44": {"statusBadge": "SEM MUDANCA DE STATUS", "ultimoStatus": "Estorno de Solicitacao"},
    "45": {"statusBadge": "CONSOLIDADO", "ultimoStatus": "Consolidacao de Coletas"},
    "49": {"statusBadge": "ENTREGUE", "ultimoStatus": "Entrega Realizada (Mobile)"},
    "51": {"statusBadge": "COLETADO NO EMBARCADOR", "ultimoStatus": "Coleta de Carga no embarcador"},
    "53": {"statusBadge": "INDENIZACAO", "ultimoStatus": "Solicitacao enviada para indenizacao"},
    "59": {"statusBadge": "CONSOLIDADO", "ultimoStatus": "Consolidacao de Entregas"},
    "60": {"statusBadge": "PROCESSADO", "ultimoStatus": "Processamento Realizado"},
    "64": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Envio de remessa cancelada para devolucao"},
    "65": {"statusBadge": "PENDENTE", "ultimoStatus": "Sinistro registrado na remessa"},
    "69": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Produtos de entrega rejeitada separados para devolucao"},
    "72": {"statusBadge": "RECEBIDO", "ultimoStatus": "Recebimento de volumes consolidados"},
    "73": {"statusBadge": "PENDENTE", "ultimoStatus": "Insucesso ao receber consolidados"},
    "77": {"statusBadge": "POSTADO", "ultimoStatus": "Objeto postado no agente de transporte"},
    "78": {"statusBadge": "AGUARDANDO RETIRADA", "ultimoStatus": "Aguardando retirada no agente de transporte"},
    "81": {"statusBadge": "DEVOLVER", "ultimoStatus": "Transferencia Devolucao Realizada"},
    "82": {"statusBadge": "LIBERADO PARA ENTREGA", "ultimoStatus": "Solicitacao Liberada para entrega"},
    "83": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Solicitacao enviada para devolucao"},
    "92": {"statusBadge": "REAGENDADO", "ultimoStatus": "Prazo alterado manualmente"},
    "94": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Carga a ser devolvida na base do parceiro"},
    "95": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Parceiro com carga em transito para devolucao"},
    "96": {"statusBadge": "PENDENTE", "ultimoStatus": "Insucesso na transferencia da devolucao"},
    "97": {"statusBadge": "DEVOLVIDO", "ultimoStatus": "Devolucao realizada pelo parceiro"},
    "98": {"statusBadge": "RECEBIDO", "ultimoStatus": "Carga Recebida"},
    "102": {"statusBadge": "PENDENTE", "ultimoStatus": "Registro de perda de volumes consolidados"},
    "104": {"statusBadge": "RECEBIDO", "ultimoStatus": "Recebimento de volumes unidade operacional"},
    "105": {"statusBadge": "PENDENTE", "ultimoStatus": "Liberado pela Fiscalizacao"},
    "108": {"statusBadge": "DEVOLUCAO", "ultimoStatus": "Recebimento do Volume para Devolucao"},
    "109": {"statusBadge": "EM ROTA", "ultimoStatus": "Volume separado para rota"},
    "111": {"statusBadge": "EM ROTA", "ultimoStatus": "Condutor em rota para coleta"},
    "112": {"statusBadge": "EM TRANSFERENCIA", "ultimoStatus": "Volumes transferido para parceiro de transporte"},
    "114": {"statusBadge": "REAGENDADO", "ultimoStatus": "Alteracao de prazo cliente"},
    "115": {"statusBadge": "EM ROTA", "ultimoStatus": "Em rota para o endereco do cliente"},
}

DE_PARA_INSUCESSO = {
    "2": "Chuvas Torrenciais",
    "3": "Rua nao Localizada",
    "4": "Numero nao Localizado",
    "7": "Desacordo com o pedido",
    "8": "Pessoa desconhecida",
    "9": "Mudanca de endereco",
    "10": "Falecimento",
    "11": "Recusada pelo cliente",
    "16": "Endereco sem acesso",
    "18": "Produto avariado no transporte",
    "19": "Fatores naturais extremos",
    "20": "Pessoa em viagem",
    "24": "Retido na fiscalizacao",
    "28": "Problemas fiscais",
    "29": "Cep incorreto",
    "30": "Suspensa pelo destinatario",
    "32": "Feriado local",
    "33": "Pessoa nao localizada no local",
    "34": "Estabelecimento/local fechado",
    "35": "Extravio",
    "36": "Furto/roubo",
    "44": "Endereco Insuficiente",
    "46": "Area de Risco",
    "56": "Cliente Ausente 2a Tentativa",
    "57": "Cliente Ausente 3a Tentativa",
    "63": "Item divergente",
    "71": "Embalagem incorreta",
    "72": "Estabelecimento reportou sinistro",
    "73": "Venda cancelada",
    "75": "Problemas no veiculo",
    "81": "Tempo Insuficiente",
    "83": "Cliente Ausente 4a Tentativa",
    "84": "Cliente Ausente 5a Tentativa",
    "86": "Setup de remessa concluido",
    "1420": "Cliente Ausente 1a Tentativa",
    "1421": "CUSTODIA",
}


def _log_debug(mensagem):
    if TMS_API_DEBUG:
        print(mensagem)


def parse_data_ocorrencia(valor):
    texto = str(valor or "").strip()
    if not texto:
        return None

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ]

    for formato in formatos:
        try:
            if formato.startswith("%Y-%m-%d") and len(texto) >= 19:
                return datetime.strptime(texto[:19], formato)
            return datetime.strptime(texto, formato)
        except ValueError:
            pass

    return None


def formatar_data_exibicao(valor):
    texto = str(valor or "").strip()
    if not texto:
        return ""

    data = parse_data_ocorrencia(texto)
    if not data:
        return texto

    if data.hour == 0 and data.minute == 0 and data.second == 0:
        return data.strftime("%d/%m/%Y")

    return data.strftime("%d/%m/%Y as %H:%M")


def ordenar_ocorrencias_por_data(resultados):
    return sorted(
        resultados,
        key=lambda item: parse_data_ocorrencia(item.get("dtOcorrencia")) or datetime.min,
    )


def normalizar_cnpj(valor):
    return re.sub(r"\D", "", str(valor or ""))


def calcular_previsao_api(resultados, cnpj_cliente="", regras_previsao=None):
    if not resultados or not regras_previsao:
        return ""

    resultados_ordenados = ordenar_ocorrencias_por_data(resultados)
    primeira = resultados_ordenados[0]
    data_base = parse_data_ocorrencia(primeira.get("dtOcorrencia"))
    if not data_base:
        return ""

    cnpj_normalizado = normalizar_cnpj(cnpj_cliente)
    uf = str(primeira.get("uf", "")).strip().upper()

    for regra in sorted(regras_previsao, key=lambda item: int(item.get("prioridade", 100))):
        tipo = str(regra.get("tipo_regra") or "").strip().upper()
        identificador = str(regra.get("identificador") or "").strip()

        if tipo == "CNPJ" and cnpj_normalizado and normalizar_cnpj(identificador) != cnpj_normalizado:
            continue

        if tipo == "UF" and uf and identificador.upper() != uf:
            continue

        if tipo not in {"CNPJ", "UF", "GERAL"}:
            continue

        dias = int(regra.get("dias_previsao", 0))
        return (data_base + timedelta(days=dias)).strftime("%d/%m/%Y")

    return ""


def _montar_resultado(codigo, cnpj_cliente, resultados, regras_previsao=None):
    resultados_ordenados = ordenar_ocorrencias_por_data(resultados)

    ocorrencia_postagem = next(
        (
            item
            for item in resultados_ordenados
            if str(item.get("codigoOcorrencia", "")).strip() == "25"
        ),
        None,
    )
    data_postagem = (
        str(ocorrencia_postagem.get("dtOcorrencia", "")).strip()
        if ocorrencia_postagem
        else None
    )

    previsao = calcular_previsao_api(resultados_ordenados, cnpj_cliente, regras_previsao)
    ultimo = resultados_ordenados[-1]

    codigo_ocorrencia = str(ultimo.get("codigoOcorrencia", "")).strip()
    descricao_api = str(ultimo.get("descricaoOcorrencia", "")).strip()
    data_ocorrencia = str(ultimo.get("dtOcorrencia", "")).strip()
    cidade = str(ultimo.get("nomeCidade", "")).strip()
    uf = str(ultimo.get("uf", "")).strip()

    depara = DE_PARA_OCORRENCIAS.get(codigo_ocorrencia, {})
    if depara:
        status_badge = depara.get("statusBadge", "Atualizado via API")
        ultimo_status = depara.get("ultimoStatus", "")
    else:
        match_insucesso = re.fullmatch(r"4\s*-\s*(\d+)", codigo_ocorrencia)
        if match_insucesso:
            motivo = DE_PARA_INSUCESSO.get(match_insucesso.group(1))
            status_badge = "DEVOLVIDO"
            if motivo:
                ultimo_status = f"Nao entregue por {motivo}"
                descricao_api = "Volume nao entregue"
            else:
                ultimo_status = "Nao entregue"
        else:
            status_badge = "Atualizado via API"
            ultimo_status = ""

    if descricao_api:
        if ultimo_status and descricao_api.lower() != ultimo_status.lower():
            ultimo_status = f"{ultimo_status} - {descricao_api}"
        elif not ultimo_status:
            ultimo_status = descricao_api

    if not ultimo_status:
        ultimo_status = f"Ocorrencia {codigo_ocorrencia}" if codigo_ocorrencia else "Ocorrencia localizada"

    ocorrencias = []
    for item in resultados_ordenados:
        cod_oc = str(item.get("codigoOcorrencia", "")).strip()
        dt_oc = str(item.get("dtOcorrencia", "")).strip()
        if not dt_oc:
            continue

        dep_oc = DE_PARA_OCORRENCIAS.get(cod_oc, {})
        if dep_oc:
            badge_oc = dep_oc.get("statusBadge", "")
        elif re.fullmatch(r"4\s*-\s*(\d+)", cod_oc):
            badge_oc = "DEVOLVIDO"
        else:
            badge_oc = ""

        ocorrencias.append({
            "codigoOcorrencia": cod_oc,
            "descricao": str(item.get("descricaoOcorrencia", "")).strip(),
            "statusBadge": badge_oc,
            "dtOcorrencia": dt_oc,
        })

    localidade = " / ".join([valor for valor in [cidade, uf] if valor]).strip()
    return {
        "codigo": codigo,
        "destinatario": localidade or "Consulta via API",
        "previsao": previsao,
        "dataBaixa": formatar_data_exibicao(data_ocorrencia),
        "recebidoPor": "",
        "ultimoStatus": ultimo_status,
        "statusBadge": status_badge,
        "dataPostagem": formatar_data_exibicao(data_postagem),
        "ocorrencias": ocorrencias,
    }


def _consultar_tms_api(payload, tipo_consulta, codigo, cnpj_cliente, headers, regras_previsao=None):
    try:
        _log_debug(f"[API] Consultando {tipo_consulta} | codigo={codigo} | cnpj={cnpj_cliente}")
        response = requests.post(
            TMS_API_URL,
            json=payload,
            headers=headers,
            timeout=TMS_API_TIMEOUT,
        )
        _log_debug(f"[API] Status HTTP ({tipo_consulta}): {response.status_code}")

        if response.status_code != 200:
            print(f"[API] HTTP {response.status_code} em {tipo_consulta} | codigo={codigo}")
            return None

        data = response.json()
        if data.get("flagErro"):
            mensagens = data.get("listaMensagens") or []
            mensagem = mensagens[0] if mensagens else "flagErro=True"
            _log_debug(f"[API] flagErro=True ({tipo_consulta}) | codigo={codigo} | mensagem={mensagem}")
            return None

        resultados = data.get("listaResultados")
        if isinstance(resultados, dict):
            resultados = [resultados]

        if not isinstance(resultados, list) or not resultados:
            return None

        return _montar_resultado(codigo, cnpj_cliente, resultados, regras_previsao)

    except requests.RequestException as exc:
        print(f"[API] Erro requests ({tipo_consulta}) no codigo {codigo}: {exc}")
        return None
    except Exception as exc:
        print(f"[API] Erro geral ({tipo_consulta}) no codigo {codigo}: {exc}")
        return None


def buscar_rastreio_na_api(codigo, cnpj_cliente, regras_previsao=None):
    """Consulta rastreio na API TMS por nota fiscal e, se nao achar, por pedido.

    Retorna um dict com os mesmos campos usados no projeto original ou None quando
    a API nao encontra resultado/retorna erro.

    regras_previsao e opcional. Exemplo:
    [{"tipo_regra": "UF", "identificador": "SP", "dias_previsao": 3, "prioridade": 1}]
    """
    codigo = str(codigo or "").strip()
    cnpj_cliente = str(cnpj_cliente or "").strip()

    if not codigo:
        print("[API] Codigo vazio")
        return None

    if not cnpj_cliente:
        print(f"[API] Codigo {codigo}: sem cnpj_cliente")
        return None

    headers = {
        "Authorization": f"Bearer {TMS_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload_nota = {
        "cnpjEmbarcador": cnpj_cliente,
        "listaNotasFiscais": [codigo],
    }
    resultado = _consultar_tms_api(
        payload_nota,
        "NOTA",
        codigo,
        cnpj_cliente,
        headers,
        regras_previsao,
    )
    if resultado:
        return resultado

    payload_pedido = {
        "cnpjEmbarcador": cnpj_cliente,
        "listaPedidos": [codigo],
    }
    return _consultar_tms_api(
        payload_pedido,
        "PEDIDO",
        codigo,
        cnpj_cliente,
        headers,
        regras_previsao,
    )


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Consulta rastreio na API TMS.")
    parser.add_argument("codigo", help="Nota fiscal ou pedido")
    parser.add_argument("cnpj", help="CNPJ do embarcador")
    args = parser.parse_args()

    print(json.dumps(buscar_rastreio_na_api(args.codigo, args.cnpj), ensure_ascii=False, indent=2))
