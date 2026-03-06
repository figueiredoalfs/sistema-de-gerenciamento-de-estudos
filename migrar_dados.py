"""
migrar_dados.py
Migra os dados do controle_desempenho.xlsx para o banco SQLite (sisfig.db).

Execute UMA UNICA VEZ antes de rodar o app Streamlit:
    python migrar_dados.py
"""

import os
import pandas as pd
from database import inicializar_banco, conectar

XLSX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "controle_desempenho.xlsx")


def migrar():
    if not os.path.exists(XLSX_PATH):
        print(f"Arquivo '{XLSX_PATH}' nao encontrado. Nada a migrar.")
        return

    # Garante que as tabelas existem
    inicializar_banco()

    print(f"Lendo {os.path.basename(XLSX_PATH)}...")

    # ── Aba LANCAMENTOS ───────────────────────────────────────────────────────
    try:
        df_l = pd.read_excel(XLSX_PATH, sheet_name="LANCAMENTOS", dtype={"ID Bateria": str})
        df_l["Acertos"]    = pd.to_numeric(df_l.get("Acertos"),    errors="coerce").fillna(0).astype(int)
        df_l["Total"]      = pd.to_numeric(df_l.get("Total"),      errors="coerce").fillna(0).astype(int)
        df_l["Percentual"] = pd.to_numeric(df_l.get("Percentual"), errors="coerce").fillna(0)
        print(f"  Lancamentos encontrados: {len(df_l)}")
    except Exception as e:
        print(f"  Erro ao ler LANCAMENTOS: {e}")
        df_l = pd.DataFrame()

    # ── Aba ERROS ─────────────────────────────────────────────────────────────
    try:
        df_e = pd.read_excel(XLSX_PATH, sheet_name="ERROS", dtype={"ID Bateria": str})
        df_e["Qtd Erros"] = pd.to_numeric(df_e.get("Qtd Erros"), errors="coerce").fillna(0).astype(int)
        print(f"  Erros encontrados      : {len(df_e)}")
    except Exception as e:
        print(f"  Erro ao ler ERROS: {e}")
        df_e = pd.DataFrame()

    # ── Aba CADASTROS ─────────────────────────────────────────────────────────
    try:
        df_c = pd.read_excel(XLSX_PATH, sheet_name="CADASTROS")
        print(f"  Cadastros encontrados  : {len(df_c)}")
    except Exception:
        print("  Nota: aba CADASTROS nao encontrada. Ignorando.")
        df_c = pd.DataFrame()

    # ── Verifica dados ja existentes no banco ─────────────────────────────────
    with conectar() as conn:
        n_l = conn.execute("SELECT COUNT(*) FROM lancamentos").fetchone()[0]
        n_e = conn.execute("SELECT COUNT(*) FROM erros").fetchone()[0]

    if n_l > 0 or n_e > 0:
        resp = input(
            f"\nJa existem dados no banco ({n_l} lancamentos, {n_e} erros).\n"
            "Deseja APAGAR tudo e reimportar? (s/n): "
        ).strip().lower()
        if resp != "s":
            print("Operacao cancelada. Banco mantido como esta.")
            return
        with conectar() as conn:
            conn.executescript(
                "DELETE FROM lancamentos; DELETE FROM erros; DELETE FROM cadastros;"
            )
        print("Dados anteriores removidos.")

    # ── Insere lancamentos ────────────────────────────────────────────────────
    n_l_ins = 0
    if not df_l.empty:
        registros = []
        for _, row in df_l.iterrows():
            registros.append({
                "id_bateria": str(row.get("ID Bateria", "")).strip(),
                "materia":    str(row.get("Materia",    "")).strip(),
                "data":       str(row.get("Data",       "")).strip(),
                "acertos":    int(row.get("Acertos",    0)),
                "total":      int(row.get("Total",      0)),
                "fonte":      str(row.get("Fonte",      "")).strip(),
                "subtopico":  str(row.get("Subtopico",  "")).strip(),
                "percentual": float(row.get("Percentual", 0)),
            })
        with conectar() as conn:
            conn.executemany(
                """INSERT INTO lancamentos
                   (id_bateria, materia, data, acertos, total, fonte, subtopico, percentual)
                   VALUES (:id_bateria, :materia, :data, :acertos, :total,
                           :fonte, :subtopico, :percentual)""",
                registros,
            )
        n_l_ins = len(registros)

    # ── Insere erros ──────────────────────────────────────────────────────────
    n_e_ins = 0
    if not df_e.empty:
        registros_e = []
        for _, row in df_e.iterrows():
            registros_e.append({
                "id_bateria":  str(row.get("ID Bateria",  "")).strip(),
                "materia":     str(row.get("Materia",     "")).strip(),
                "topico":      str(row.get("Topico",      "")).strip(),
                "qtd_erros":   int(row.get("Qtd Erros",   1)),
                "data":        str(row.get("Data",         "")).strip(),
                "observacao":  str(row.get("Observacao",  "")).strip(),
                "providencia": str(row.get("Providencia", "")).strip(),
            })
        with conectar() as conn:
            conn.executemany(
                """INSERT INTO erros
                   (id_bateria, materia, topico, qtd_erros, data, observacao, providencia)
                   VALUES (:id_bateria, :materia, :topico, :qtd_erros,
                           :data, :observacao, :providencia)""",
                registros_e,
            )
        n_e_ins = len(registros_e)

    # ── Insere cadastros ──────────────────────────────────────────────────────
    n_c_ins = 0
    if not df_c.empty and "Materia" in df_c.columns:
        pares = []
        for _, row in df_c.iterrows():
            mat = str(row.get("Materia", "")).strip()
            ass = str(row.get("Assunto", "")).strip()
            if mat:
                pares.append((mat, ass))
        if pares:
            with conectar() as conn:
                conn.executemany(
                    "INSERT INTO cadastros (materia, assunto) VALUES (?, ?)",
                    pares,
                )
            n_c_ins = len(pares)

    # ── Resumo ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("MIGRACAO CONCLUIDA")
    print("=" * 55)
    print(f"  Lancamentos importados : {n_l_ins}")
    print(f"  Erros importados       : {n_e_ins}")
    print(f"  Cadastros importados   : {n_c_ins}")
    print(f"\nBanco salvo em: sisfig.db")
    print("Agora rode: streamlit run app.py")
    print("=" * 55)


if __name__ == "__main__":
    migrar()
