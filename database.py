"""
database.py
Conexao com SQLite e todas as funcoes CRUD do SISFIG.
Banco de dados: sisfig.db (criado automaticamente na primeira execucao).
"""

import sqlite3
import pandas as pd

DB_PATH = "sisfig.db"


def conectar() -> sqlite3.Connection:
    """Retorna uma conexao com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco():
    """Cria as tabelas se ainda nao existirem. Chamado na inicializacao do app."""
    with conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id_bateria  TEXT NOT NULL,
                materia     TEXT NOT NULL,
                data        TEXT,
                acertos     INTEGER DEFAULT 0,
                total       INTEGER DEFAULT 0,
                fonte       TEXT,
                subtopico   TEXT,
                percentual  REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS erros (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                id_bateria  TEXT NOT NULL,
                materia     TEXT NOT NULL,
                topico      TEXT NOT NULL,
                qtd_erros   INTEGER DEFAULT 1,
                data        TEXT,
                observacao  TEXT,
                providencia TEXT
            );

            CREATE TABLE IF NOT EXISTS cadastros (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                materia TEXT NOT NULL,
                assunto TEXT DEFAULT ''
            );
        """)


# ─── LANCAMENTOS ──────────────────────────────────────────────────────────────

def gerar_proximo_id() -> str:
    """Gera o proximo ID de bateria no formato B001, B002, ..."""
    with conectar() as conn:
        rows = conn.execute(
            "SELECT id_bateria FROM lancamentos"
        ).fetchall()
    nums = []
    for row in rows:
        try:
            nums.append(int(str(row["id_bateria"]).lstrip("Bb")))
        except ValueError:
            pass
    return f"B{(max(nums) + 1):03d}" if nums else "B001"


def inserir_lancamentos(registros: list):
    """
    Insere uma lista de lancamentos de uma vez (ao finalizar a bateria).
    Cada item deve ser um dict com: id_bateria, materia, data, acertos,
    total, fonte, subtopico, percentual.
    """
    with conectar() as conn:
        conn.executemany(
            """INSERT INTO lancamentos
               (id_bateria, materia, data, acertos, total, fonte, subtopico, percentual)
               VALUES (:id_bateria, :materia, :data, :acertos, :total,
                       :fonte, :subtopico, :percentual)""",
            registros,
        )


def inserir_erro(dados: dict):
    """Insere um registro de erro."""
    with conectar() as conn:
        conn.execute(
            """INSERT INTO erros
               (id_bateria, materia, topico, qtd_erros, data, observacao, providencia)
               VALUES (:id_bateria, :materia, :topico, :qtd_erros,
                       :data, :observacao, :providencia)""",
            dados,
        )


def ler_lancamentos() -> pd.DataFrame:
    """Retorna todos os lancamentos como DataFrame com nomes de colunas padrao."""
    with conectar() as conn:
        df = pd.read_sql_query(
            """SELECT id_bateria, materia, data, acertos, total,
                      fonte, subtopico, percentual
               FROM lancamentos""",
            conn,
        )
    df.rename(columns={
        "id_bateria": "ID Bateria",
        "materia":    "Materia",
        "data":       "Data",
        "acertos":    "Acertos",
        "total":      "Total",
        "fonte":      "Fonte",
        "subtopico":  "Subtopico",
        "percentual": "Percentual",
    }, inplace=True)
    df["Acertos"]   = pd.to_numeric(df["Acertos"],   errors="coerce").fillna(0).astype(int)
    df["Total"]     = pd.to_numeric(df["Total"],     errors="coerce").fillna(0).astype(int)
    df["Percentual"]= pd.to_numeric(df["Percentual"],errors="coerce").fillna(0)
    return df


def ler_erros() -> pd.DataFrame:
    """Retorna todos os erros como DataFrame com nomes de colunas padrao."""
    with conectar() as conn:
        df = pd.read_sql_query(
            """SELECT id_bateria, materia, topico, qtd_erros,
                      data, observacao, providencia
               FROM erros""",
            conn,
        )
    df.rename(columns={
        "id_bateria":  "ID Bateria",
        "materia":     "Materia",
        "topico":      "Topico",
        "qtd_erros":   "Qtd Erros",
        "data":        "Data",
        "observacao":  "Observacao",
        "providencia": "Providencia",
    }, inplace=True)
    df["Qtd Erros"] = pd.to_numeric(df["Qtd Erros"], errors="coerce").fillna(0).astype(int)
    return df


# ─── CADASTROS ────────────────────────────────────────────────────────────────

def get_materias() -> list:
    """Retorna lista de materias unicas cadastradas, em ordem alfabetica."""
    with conectar() as conn:
        rows = conn.execute(
            "SELECT DISTINCT materia FROM cadastros ORDER BY materia"
        ).fetchall()
    return [r["materia"] for r in rows]


def get_assuntos(materia: str) -> list:
    """Retorna lista de assuntos de uma materia (exclui entradas vazias)."""
    with conectar() as conn:
        rows = conn.execute(
            """SELECT assunto FROM cadastros
               WHERE materia = ? AND assunto != ''
               ORDER BY assunto""",
            (materia,),
        ).fetchall()
    return [r["assunto"] for r in rows]


def inserir_materia(materia: str):
    """Cria uma materia sem assunto (linha sentinela para garantir aparicao na lista)."""
    with conectar() as conn:
        conn.execute(
            "INSERT INTO cadastros (materia, assunto) VALUES (?, '')",
            (materia,),
        )


def inserir_assunto(materia: str, assunto: str):
    """Adiciona um assunto a uma materia existente."""
    with conectar() as conn:
        conn.execute(
            "INSERT INTO cadastros (materia, assunto) VALUES (?, ?)",
            (materia, assunto),
        )


def remover_assunto(materia: str, assunto: str):
    """Remove um assunto especifico de uma materia."""
    with conectar() as conn:
        conn.execute(
            "DELETE FROM cadastros WHERE materia = ? AND assunto = ?",
            (materia, assunto),
        )


def remover_materia(materia: str):
    """Remove uma materia e todos os seus assuntos."""
    with conectar() as conn:
        conn.execute("DELETE FROM cadastros WHERE materia = ?", (materia,))
