"""
migrar_dev_para_railway.py
--------------------------
Migra matérias (topicos), subtópicos, questões e ciclos do dev.db (SQLite)
para o PostgreSQL do Railway.

Uso:
    python migrar_dev_para_railway.py --pg-url "postgresql://user:pass@host:5432/db"
    # ou defina a variável de ambiente RAILWAY_DATABASE_URL

Tabelas migradas (nesta ordem):
    1. topicos        — nivel 0 (matéria), 1 (bloco), 2 (subtópico)
    2. questoes
    3. ciclo_materias
"""

import argparse
import os
import sqlite3
import sys

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERRO: psycopg2 não encontrado. Instale com: pip install psycopg2-binary")
    sys.exit(1)

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "dev.db")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def sqlite_rows(sqlite_conn, table: str, order_by: str = "rowid"):
    """Retorna todas as linhas de uma tabela SQLite como lista de dicts."""
    cur = sqlite_conn.cursor()
    cur.execute(f"SELECT * FROM {table} ORDER BY {order_by}")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def upsert_pg(pg_conn, table: str, rows: list[dict], conflict_col: str = "id"):
    """INSERT ... ON CONFLICT (conflict_col) DO UPDATE SET ... para cada row."""
    if not rows:
        return 0

    cols = list(rows[0].keys())
    cols_str = ", ".join(cols)
    placeholders = ", ".join([f"%({c})s" for c in cols])
    update_set = ", ".join(
        [f"{c} = EXCLUDED.{c}" for c in cols if c != conflict_col]
    )

    sql = (
        f"INSERT INTO {table} ({cols_str}) "
        f"VALUES ({placeholders}) "
        f"ON CONFLICT ({conflict_col}) DO UPDATE SET {update_set}"
    )

    cur = pg_conn.cursor()
    psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
    pg_conn.commit()
    return len(rows)


def table_exists(sqlite_conn, table: str) -> bool:
    cur = sqlite_conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cur.fetchone() is not None


# ──────────────────────────────────────────────────────────────────────────────
# Migração por tabela
# ──────────────────────────────────────────────────────────────────────────────

TOPICO_COLS = [
    "id", "parent_id", "nivel", "nome", "descricao", "area", "banca",
    "peso_edital", "decay_rate", "dependencias_json", "prerequisitos_json",
    "ativo", "created_at",
]

QUESTAO_COLS = [
    "id", "subject_id", "topic_id", "subtopic_id", "enunciado",
    "alternativas_json", "resposta_correta", "fonte", "banca", "ano",
    "ativo", "created_at",
]

CICLO_COLS = [
    "id", "area", "subject_id", "ordem", "ativo", "created_at", "updated_at",
]

QUESTAO_BANCO_COLS = [
    "id", "question_code", "materia", "subject", "statement",
    "alternatives_json", "correct_answer", "board", "year",
    "materia_pendente", "created_at",
]


BOOL_COLS = {"ativo", "uma_vez", "concluida", "materia_pendente"}

def filter_cols(row: dict, cols: list[str]) -> dict:
    """Retorna apenas as colunas esperadas, preenchendo ausentes com None.
    Converte inteiros SQLite (0/1) para bool Python onde necessário."""
    result = {}
    for c in cols:
        v = row.get(c)
        if c in BOOL_COLS and isinstance(v, int):
            v = bool(v)
        result[c] = v
    return result


def migrar_topicos(sqlite_conn, pg_conn):
    if not table_exists(sqlite_conn, "topicos"):
        print("  [SKIP] tabela 'topicos' não encontrada no SQLite")
        return 0

    rows = sqlite_rows(sqlite_conn, "topicos")
    # Ordenar: parents antes de filhos (nivel crescente garante isso)
    rows.sort(key=lambda r: (r.get("nivel") or 0))
    rows = [filter_cols(r, TOPICO_COLS) for r in rows]
    n = upsert_pg(pg_conn, "topicos", rows)
    return n


def migrar_questoes(sqlite_conn, pg_conn):
    if not table_exists(sqlite_conn, "questoes"):
        print("  [SKIP] tabela 'questoes' não encontrada no SQLite")
        return 0

    rows = sqlite_rows(sqlite_conn, "questoes")
    rows = [filter_cols(r, QUESTAO_COLS) for r in rows]

    # Garantir que 'fonte' seja um valor válido do ENUM
    FONTES_VALIDAS = {"ia", "admin", "qconcursos", "tec", "prova_real", "simulado"}
    for r in rows:
        if r.get("fonte") not in FONTES_VALIDAS:
            r["fonte"] = "admin"

    n = upsert_pg(pg_conn, "questoes", rows)
    return n


def migrar_questoes_banco(sqlite_conn, pg_conn):
    if not table_exists(sqlite_conn, "questoes_banco"):
        print("  [SKIP] tabela 'questoes_banco' não encontrada no SQLite")
        return 0

    rows = sqlite_rows(sqlite_conn, "questoes_banco")
    rows = [filter_cols(r, QUESTAO_BANCO_COLS) for r in rows]
    for r in rows:
        if r.get("question_code") and len(r["question_code"]) > 50:
            r["question_code"] = r["question_code"][:50]
    n = upsert_pg(pg_conn, "questoes_banco", rows, conflict_col="question_code")
    return n


def migrar_ciclos(sqlite_conn, pg_conn):
    if not table_exists(sqlite_conn, "ciclo_materias"):
        print("  [SKIP] tabela 'ciclo_materias' não encontrada no SQLite")
        return 0

    rows = sqlite_rows(sqlite_conn, "ciclo_materias")
    rows = [filter_cols(r, CICLO_COLS) for r in rows]
    n = upsert_pg(pg_conn, "ciclo_materias", rows)
    return n


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Migra dev.db → Railway PostgreSQL")
    parser.add_argument(
        "--pg-url",
        default=os.environ.get("RAILWAY_DATABASE_URL", ""),
        help="URL do PostgreSQL Railway (ou defina RAILWAY_DATABASE_URL)",
    )
    parser.add_argument(
        "--sqlite",
        default=SQLITE_PATH,
        help=f"Caminho do dev.db (padrão: {SQLITE_PATH})",
    )
    args = parser.parse_args()

    pg_url = args.pg_url.strip()
    if not pg_url:
        print(
            "ERRO: informe a URL do PostgreSQL via --pg-url ou RAILWAY_DATABASE_URL.\n"
            "Exemplo: postgresql://user:pass@host.railway.app:5432/railway"
        )
        sys.exit(1)

    # Fix Railway: postgres:// → postgresql://
    pg_url = pg_url.replace("postgres://", "postgresql://", 1)

    if not os.path.exists(args.sqlite):
        print(f"ERRO: arquivo SQLite não encontrado: {args.sqlite}")
        sys.exit(1)

    print(f"SQLite : {args.sqlite}")
    print(f"PG host: {pg_url.split('@')[-1] if '@' in pg_url else pg_url}")
    print()

    sqlite_conn = sqlite3.connect(args.sqlite)
    sqlite_conn.row_factory = sqlite3.Row

    try:
        pg_conn = psycopg2.connect(pg_url, sslmode="require")
    except psycopg2.OperationalError as e:
        # Railway internal não usa SSL
        try:
            pg_conn = psycopg2.connect(pg_url)
        except Exception:
            print(f"ERRO ao conectar ao PostgreSQL: {e}")
            sys.exit(1)

    print("Conectado. Iniciando migração...\n")

    try:
        print("1/3  Migrando tópicos...")
        n = migrar_topicos(sqlite_conn, pg_conn)
        print(f"     {n} registros upserted em 'topicos'\n")

        print("2/3  Migrando questões (questoes)...")
        n = migrar_questoes(sqlite_conn, pg_conn)
        print(f"     {n} registros upserted em 'questoes'\n")

        print("3/3  Migrando questões do banco (questoes_banco)...")
        n = migrar_questoes_banco(sqlite_conn, pg_conn)
        print(f"     {n} registros upserted em 'questoes_banco'\n")

        print("4/4  Migrando ciclos de matérias...")
        n = migrar_ciclos(sqlite_conn, pg_conn)
        print(f"     {n} registros upserted em 'ciclo_materias'\n")

        print("✅  Migração concluída com sucesso.")
        print()
        print("Verificar no Railway:")
        print("  GET /admin/topicos   — lista de matérias e subtópicos")
        print("  GET /admin/questoes  — banco de questões")

    except Exception as e:
        pg_conn.rollback()
        print(f"\nERRO durante a migração: {e}")
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
