import sqlite3
import pandas as pd


DB_PATH = "database.db"
ARQUIVO_SAIDA = "exportacao_completa_teste.xlsx"


def main():
    conn = sqlite3.connect(DB_PATH)

    tabelas = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
        conn
    )

    with pd.ExcelWriter(ARQUIVO_SAIDA, engine="openpyxl") as writer:
        for nome_tabela in tabelas["name"]:
            df = pd.read_sql_query(f"SELECT * FROM {nome_tabela}", conn)
            df.to_excel(writer, sheet_name=nome_tabela[:31], index=False)

    conn.close()
    print(f"Exportação concluída com sucesso: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()