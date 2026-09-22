from __future__ import annotations

import argparse
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DB_PATH = Path("/home/rastreamento/database.db")
ENTRADA_DIR = Path("/home/cliente_sftp/AGYLOG/RETORNOOMELETE")
PROCESSADOS_DIR = ENTRADA_DIR / "processados"
STATUS_CRIACAO = "1"


@dataclass(frozen=True)
class CampoFixo:
    nome: str
    inicio: int
    tamanho: int


LAYOUT_342 = (
    CampoFixo("identificador", 1, 3),
    CampoFixo("cnpj_emitente", 4, 14),
    CampoFixo("serie_nota", 18, 3),
    CampoFixo("numero_nota", 21, 8),
    CampoFixo("codigo_ocorrencia", 29, 2),
    CampoFixo("data_ocorrencia", 31, 8),
    CampoFixo("hora_ocorrencia", 39, 4),
    CampoFixo("codigo_observacao", 43, 2),
    CampoFixo("texto_livre", 45, 70),
    CampoFixo("codigo_ar_pedido", 115, 27),
)


def extrair_campo(linha: str, campo: CampoFixo) -> str:
    inicio = campo.inicio - 1
    return linha[inicio : inicio + campo.tamanho].strip()


def parse_linha_342(linha: str) -> dict[str, str]:
    return {campo.nome: extrair_campo(linha, campo) for campo in LAYOUT_342}


def normalizar_codigo(valor: str) -> str:
    return str(valor or "").strip().upper()


def normalizar_cnpj(valor: str) -> str | None:
    cnpj = "".join(ch for ch in str(valor or "") if ch.isdigit())
    return cnpj or None


def normalizar_numero(valor: str) -> str | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    sem_zeros = texto.lstrip("0")
    return sem_zeros or texto


def normalizar_ocorrencia(valor: str) -> str:
    texto = str(valor or "").strip()
    if texto.isdigit():
        return str(int(texto))
    return texto


def formatar_data_hora_ocorrencia(data: str, hora: str) -> str | None:
    data_digits = "".join(ch for ch in str(data or "") if ch.isdigit())
    hora_digits = "".join(ch for ch in str(hora or "") if ch.isdigit())

    if len(data_digits) != 8:
        return None

    if len(hora_digits) == 0:
        hora_digits = "0000"
    elif len(hora_digits) < 4:
        hora_digits = hora_digits.zfill(4)
    else:
        hora_digits = hora_digits[:4]

    try:
        return datetime.strptime(data_digits + hora_digits, "%d%m%Y%H%M").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return None


def ler_rastreios_proceda(arquivo: Path) -> list[dict[str, str | None]]:
    rastreios: list[dict[str, str | None]] = []
    vistos: set[str] = set()

    with arquivo.open("r", encoding="utf-8", errors="replace") as entrada:
        for numero_linha, linha in enumerate(entrada, start=1):
            linha = linha.rstrip("\r\n")
            if not linha.startswith("342"):
                continue

            registro = parse_linha_342(linha)
            if normalizar_ocorrencia(registro["codigo_ocorrencia"]) != STATUS_CRIACAO:
                continue

            codigo = normalizar_codigo(registro["codigo_ar_pedido"])
            if not codigo:
                print(f"{arquivo.name}:{numero_linha}: ignorado sem codigo AR/Pedido.")
                continue
            if codigo in vistos:
                continue

            vistos.add(codigo)
            rastreios.append(
                {
                    "codigo": codigo,
                    "cnpj_cliente": normalizar_cnpj(registro["cnpj_emitente"]),
                    "nota_fiscal": normalizar_numero(registro["numero_nota"]),
                    "serie_nota_fiscal": normalizar_numero(registro["serie_nota"]),
                    "data_cadastro_portal": formatar_data_hora_ocorrencia(
                        registro["data_ocorrencia"],
                        registro["hora_ocorrencia"],
                    ),
                }
            )

    return rastreios


def criar_backup_banco(caminho_banco: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = caminho_banco.with_name(f"{caminho_banco.name}.bak_omelete_{timestamp}")
    shutil.copy2(caminho_banco, backup)
    return backup


def listar_arquivos(entrada_dir: Path) -> list[Path]:
    return sorted(
        arquivo
        for arquivo in entrada_dir.glob("*.txt")
        if arquivo.is_file() and not arquivo.name.startswith(".")
    )


def importar_arquivos(
    entrada_dir: Path,
    db_path: Path,
    destinatario_padrao: str,
    dry_run: bool,
    mover_processados: bool,
    criar_backup: bool,
) -> tuple[int, int, int, int]:
    arquivos = listar_arquivos(entrada_dir)
    if not arquivos:
        print(f"Nenhum .txt encontrado em {entrada_dir}")
        return 0, 0, 0, 0

    registros_por_arquivo = [(arquivo, ler_rastreios_proceda(arquivo)) for arquivo in arquivos]
    total_lidos = sum(len(registros) for _, registros in registros_por_arquivo)

    if dry_run:
        print(f"Simulacao: {len(arquivos)} arquivo(s), {total_lidos} rastreio(s) lido(s).")
        return len(arquivos), total_lidos, 0, 0

    if not db_path.exists():
        raise FileNotFoundError(f"Banco nao encontrado: {db_path}")

    if criar_backup:
        backup = criar_backup_banco(db_path)
        print(f"Backup criado: {backup}")

    conn = sqlite3.connect(db_path)
    try:
        inseridos = 0
        existentes = 0
        for _, registros in registros_por_arquivo:
            for registro in registros:
                data_cadastro = registro["data_cadastro_portal"] or datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO rastreios (
                        codigo,
                        destinatario,
                        data_cadastro_portal,
                        ultimo_status,
                        status_badge,
                        cnpj_cliente,
                        nota_fiscal,
                        serie_nota_fiscal
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        registro["codigo"],
                        destinatario_padrao,
                        data_cadastro,
                        "Criação da solicitação",
                        "CRIADO",
                        registro["cnpj_cliente"],
                        registro["nota_fiscal"],
                        registro["serie_nota_fiscal"],
                    ),
                )
                if cursor.rowcount:
                    inseridos += 1
                else:
                    existentes += 1

        conn.commit()

        if mover_processados:
            PROCESSADOS_DIR.mkdir(parents=True, exist_ok=True)
            for arquivo, _ in registros_por_arquivo:
                destino = PROCESSADOS_DIR / arquivo.name
                if destino.exists():
                    destino = PROCESSADOS_DIR / f"{arquivo.stem}_{datetime.now():%Y%m%d_%H%M%S}{arquivo.suffix}"
                arquivo.replace(destino)

        return len(arquivos), total_lidos, inseridos, existentes
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cadastra rastreios do PROCEDA OMELETE no banco do portal."
    )
    parser.add_argument("--entrada-dir", type=Path, default=ENTRADA_DIR)
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--destinatario-padrao", default="-")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sem-backup", action="store_true")
    parser.add_argument("--mover-processados", action="store_true")
    args = parser.parse_args()

    arquivos, lidos, inseridos, existentes = importar_arquivos(
        args.entrada_dir,
        args.db,
        args.destinatario_padrao,
        args.dry_run,
        args.mover_processados,
        not args.sem_backup,
    )

    print("Importacao PROCEDA OMELETE concluida.")
    print(f"Arquivos lidos: {arquivos}")
    print(f"Rastreios encontrados: {lidos}")
    print(f"Inseridos: {inseridos}")
    print(f"Ja existiam: {existentes}")


if __name__ == "__main__":
    main()
