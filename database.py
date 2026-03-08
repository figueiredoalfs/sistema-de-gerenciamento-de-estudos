"""
database.py
Conexao com SQLite e todas as funcoes CRUD do SISFIG.
Banco de dados: sisfig.db (criado automaticamente na primeira execucao).
"""

import sqlite3
import hashlib
import os
import pandas as pd

DB_PATH = "sisfig.db"


def _hash_senha(senha: str, salt: str = "") -> str:
    """Gera hash SHA-256 da senha com salt."""
    raw = (salt + senha).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verificar_login(email: str, senha: str) -> dict | None:
    """
    Verifica credenciais. Retorna dict com id, nome, email, role
    ou None se invalido.
    """
    with conectar() as conn:
        row = conn.execute(
            "SELECT id, nome, email, senha_hash, role FROM usuarios WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    if row and row["senha_hash"] == _hash_senha(senha, row["email"]):
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "role": row["role"]}
    return None


def criar_usuario(nome: str, email: str, senha: str, role: str = "aluno") -> bool:
    """Cria usuario. Retorna False se email ja existe."""
    email = email.strip().lower()
    try:
        with conectar() as conn:
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (?, ?, ?, ?)",
                (nome, email, _hash_senha(senha, email), role),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_perfil(usuario_id: int) -> dict:
    """Retorna todos os campos de perfil do usuario."""
    with conectar() as conn:
        row = conn.execute(
            """SELECT id, nome, email, role,
                      telefone, cpf, data_nascimento,
                      cep, endereco, numero, complemento, bairro, cidade, estado,
                      plano
               FROM usuarios WHERE id = ?""",
            (usuario_id,),
        ).fetchone()
    if row:
        return dict(row)
    return {}


def salvar_perfil(usuario_id: int, dados: dict) -> bool:
    """Atualiza dados pessoais/endereco/plano. Nao altera senha_hash diretamente."""
    campos_permitidos = {
        "nome", "telefone", "cpf", "data_nascimento",
        "cep", "endereco", "numero", "complemento", "bairro", "cidade", "estado",
        "plano",
    }
    updates = {k: v for k, v in dados.items() if k in campos_permitidos}
    if not updates:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    valores = list(updates.values()) + [usuario_id]
    with conectar() as conn:
        conn.execute(f"UPDATE usuarios SET {set_clause} WHERE id = ?", valores)
    return True


def alterar_email(usuario_id: int, novo_email: str, senha_atual: str) -> str:
    """
    Altera o email apos verificar a senha atual.
    Retorna 'ok', 'senha_errada' ou 'email_em_uso'.
    """
    novo_email = novo_email.strip().lower()
    with conectar() as conn:
        row = conn.execute(
            "SELECT email, senha_hash FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        if not row:
            return "senha_errada"
        if row["senha_hash"] != _hash_senha(senha_atual, row["email"]):
            return "senha_errada"
        em_uso = conn.execute(
            "SELECT 1 FROM usuarios WHERE email = ? AND id != ?", (novo_email, usuario_id)
        ).fetchone()
        if em_uso:
            return "email_em_uso"
        conn.execute(
            "UPDATE usuarios SET email = ?, senha_hash = ? WHERE id = ?",
            (novo_email, _hash_senha(senha_atual, novo_email), usuario_id),
        )
    return "ok"


def alterar_senha(usuario_id: int, senha_atual: str, nova_senha: str) -> bool:
    """Altera a senha apos verificar a senha atual. Retorna True se ok."""
    with conectar() as conn:
        row = conn.execute(
            "SELECT email, senha_hash FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        if not row or row["senha_hash"] != _hash_senha(senha_atual, row["email"]):
            return False
        conn.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (_hash_senha(nova_senha, row["email"]), usuario_id),
        )
    return True


def conectar() -> sqlite3.Connection:
    """Retorna uma conexao com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco():
    """Cria as tabelas se ainda nao existirem. Chamado na inicializacao do app."""
    with conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT NOT NULL,
                email      TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                role       TEXT NOT NULL DEFAULT 'aluno'
            );
        """)
        # Cria admin padrao se nao existir
        existe = conn.execute(
            "SELECT 1 FROM usuarios WHERE email = 'admin@aprovai.com'"
        ).fetchone()
        if not existe:
            email = "admin@aprovai.com"
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (?, ?, ?, ?)",
                ("Admin", email, _hash_senha("admin123", email), "admin"),
            )

        # Adiciona colunas de perfil se ainda nao existirem (migracao incremental)
        colunas_perfil = [
            ("telefone",        "TEXT DEFAULT ''"),
            ("cpf",             "TEXT DEFAULT ''"),
            ("data_nascimento", "TEXT DEFAULT ''"),
            ("cep",             "TEXT DEFAULT ''"),
            ("endereco",        "TEXT DEFAULT ''"),
            ("numero",          "TEXT DEFAULT ''"),
            ("complemento",     "TEXT DEFAULT ''"),
            ("bairro",          "TEXT DEFAULT ''"),
            ("cidade",          "TEXT DEFAULT ''"),
            ("estado",          "TEXT DEFAULT ''"),
            ("plano",           "TEXT DEFAULT 'gratuito'"),
        ]
        colunas_existentes = {row[1] for row in conn.execute("PRAGMA table_info(usuarios)").fetchall()}
        for col, tipo in colunas_perfil:
            if col not in colunas_existentes:
                conn.execute(f"ALTER TABLE usuarios ADD COLUMN {col} {tipo}")
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
