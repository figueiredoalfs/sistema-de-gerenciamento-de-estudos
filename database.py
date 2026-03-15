"""
database.py
Conexao com SQLite e todas as funcoes CRUD do SISFIG.
Banco de dados: sisfig.db (criado automaticamente na primeira execucao).
"""

import sqlite3
import hashlib
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sisfig.db")

# ─── CATÁLOGO PADRÃO ──────────────────────────────────────────────────────────
# Derivado de config_materias.HIERARQUIA — fonte única de verdade.
# Para adicionar/remover matérias, edite config_materias.py.

from config_materias import HIERARQUIA as _HIERARQUIA
MATERIAS_PADRAO: dict[str, list[str]] = {
    mat: list(topicos.keys())
    for mat, topicos in _HIERARQUIA.items()
}


def _hash_senha(senha: str, salt: str = "") -> str:
    """Gera hash SHA-256 da senha com salt."""
    raw = (salt + senha).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verificar_login(email: str, senha: str) -> dict | None:
    """
    Verifica credenciais. Retorna dict com id, nome, email, role ou None.
    Senha vazia é aceita em modo dev (qualquer usuário entra sem senha).
    """
    with conectar() as conn:
        row = conn.execute(
            "SELECT id, nome, email, senha_hash, role, email_confirmado FROM usuarios WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    if not row:
        return None
    senha_ok = (senha == "") or (row["senha_hash"] == _hash_senha(senha, row["email"]))
    if senha_ok:
        return {
            "id": row["id"], "nome": row["nome"], "email": row["email"], "role": row["role"],
            "email_confirmado": bool(row["email_confirmado"] if row["email_confirmado"] is not None else 1),
        }
    return None


def criar_usuario(nome: str, email: str, senha: str, role: str = "estudante") -> bool:
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
                      plano, area_estudo, horas_dia, dias_semana, perfil_estudo, data_prova
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
        "plano", "area_estudo", "horas_dia", "dias_semana", "perfil_estudo", "data_prova",
    }
    updates = {k: v for k, v in dados.items() if k in campos_permitidos}
    if not updates:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    valores = list(updates.values()) + [usuario_id]
    with conectar() as conn:
        conn.execute(f"UPDATE usuarios SET {set_clause} WHERE id = ?", valores)
    return True


def get_plataformas_ativas(usuario_id: int) -> list:
    """Retorna lista de slugs de plataformas ativas do usuário."""
    import json
    from config_fontes import PLATAFORMAS_DEFAULT
    with conectar() as conn:
        row = conn.execute(
            "SELECT plataformas_ativas FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    if not row or not row["plataformas_ativas"]:
        return PLATAFORMAS_DEFAULT
    try:
        return json.loads(row["plataformas_ativas"])
    except Exception:
        return PLATAFORMAS_DEFAULT


def salvar_plataformas_ativas(usuario_id: int, slugs: list):
    """Salva lista de slugs de plataformas ativas do usuário."""
    import json
    with conectar() as conn:
        conn.execute(
            "UPDATE usuarios SET plataformas_ativas = ? WHERE id = ?",
            (json.dumps(slugs), usuario_id),
        )


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
        # Remove admins antigos e garante admin único com login "admin"
        for old in ("admin@aprovai.com", "admin@concursoai.com", "admin@skolai.com"):
            conn.execute("DELETE FROM usuarios WHERE email = ?", (old,))
        existe = conn.execute(
            "SELECT 1 FROM usuarios WHERE email = 'admin'"
        ).fetchone()
        if not existe:
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (?, ?, ?, ?)",
                ("Admin", "admin", _hash_senha("", "admin"), "administrador"),
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
            ("area_estudo",     "TEXT DEFAULT ''"),
            ("horas_dia",       "REAL DEFAULT 3.0"),
            ("dias_semana",     "INTEGER DEFAULT 5"),
            ("perfil_estudo",   "TEXT DEFAULT 'zero'"),
            ("data_prova",      "TEXT DEFAULT ''"),
        ]
        colunas_existentes = {row[1] for row in conn.execute("PRAGMA table_info(usuarios)").fetchall()}
        for col, tipo in colunas_perfil:
            if col not in colunas_existentes:
                conn.execute(f"ALTER TABLE usuarios ADD COLUMN {col} {tipo}")

        # Colunas para confirmação de e-mail (ativada via EMAIL_CONFIRMACAO=true no Railway)
        cols_confirmacao = [
            ("email_confirmado",  "INTEGER DEFAULT 1"),   # 1=confirmado; legados e dev ficam confirmados
            ("token_confirmacao", "TEXT DEFAULT NULL"),
        ]
        for col, tipo in cols_confirmacao:
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
                percentual  REAL DEFAULT 0,
                usuario_id  INTEGER
            );

            CREATE TABLE IF NOT EXISTS erros (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                id_bateria  TEXT NOT NULL,
                materia     TEXT NOT NULL,
                topico      TEXT NOT NULL,
                qtd_erros   INTEGER DEFAULT 1,
                data        TEXT,
                observacao  TEXT,
                providencia TEXT,
                usuario_id  INTEGER
            );

            CREATE TABLE IF NOT EXISTS cadastros (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                materia    TEXT NOT NULL,
                assunto    TEXT DEFAULT '',
                usuario_id INTEGER
            );
        """)

        # Adiciona usuario_id nas tabelas existentes (migracao incremental)
        for tabela in ("lancamentos", "erros", "cadastros"):
            cols = {r[1] for r in conn.execute(f"PRAGMA table_info({tabela})").fetchall()}
            if "usuario_id" not in cols:
                conn.execute(f"ALTER TABLE {tabela} ADD COLUMN usuario_id INTEGER")

        # Adiciona colunas de diagnostico na tabela erros (migracao incremental)
        cols_erros = {r[1] for r in conn.execute("PRAGMA table_info(erros)").fetchall()}
        if "tipo_erro" not in cols_erros:
            conn.execute("ALTER TABLE erros ADD COLUMN tipo_erro TEXT DEFAULT 'nao_sabia'")
        if "status" not in cols_erros:
            conn.execute("ALTER TABLE erros ADD COLUMN status TEXT DEFAULT 'pendente'")
        if "subtopico_erro" not in cols_erros:
            conn.execute("ALTER TABLE erros ADD COLUMN subtopico_erro TEXT DEFAULT ''")

        # Adiciona plataformas_ativas em usuarios (migracao incremental)
        cols_usr = {r[1] for r in conn.execute("PRAGMA table_info(usuarios)").fetchall()}
        if "plataformas_ativas" not in cols_usr:
            conn.execute(
                "ALTER TABLE usuarios ADD COLUMN plataformas_ativas TEXT DEFAULT '[]'"
            )

        # Migração de roles: nomes antigos → novos (idempotente)
        conn.execute("UPDATE usuarios SET role = 'estudante'     WHERE role = 'aluno'")
        conn.execute("UPDATE usuarios SET role = 'administrador' WHERE role = 'admin'")


# ─── LANCAMENTOS ──────────────────────────────────────────────────────────────

def gerar_proximo_id(usuario_id: int) -> str:
    """Gera o proximo ID de bateria do usuario no formato B001, B002, ..."""
    with conectar() as conn:
        rows = conn.execute(
            "SELECT id_bateria FROM lancamentos WHERE usuario_id = ?", (usuario_id,)
        ).fetchall()
    nums = []
    for row in rows:
        try:
            nums.append(int(str(row["id_bateria"]).lstrip("Bb")))
        except ValueError:
            pass
    return f"B{(max(nums) + 1):03d}" if nums else "B001"


def inserir_lancamentos(registros: list, usuario_id: int):
    """Insere lancamentos do usuario. Cada item: id_bateria, materia, data,
    acertos, total, fonte, subtopico, percentual."""
    for r in registros:
        r["usuario_id"] = usuario_id
    with conectar() as conn:
        conn.executemany(
            """INSERT INTO lancamentos
               (id_bateria, materia, data, acertos, total, fonte, subtopico, percentual, usuario_id)
               VALUES (:id_bateria, :materia, :data, :acertos, :total,
                       :fonte, :subtopico, :percentual, :usuario_id)""",
            registros,
        )


def inserir_erro(dados: dict, usuario_id: int):
    """Insere um registro de erro do usuario."""
    dados["usuario_id"] = usuario_id
    dados.setdefault("tipo_erro", "nao_sabia")
    dados.setdefault("status", "pendente")
    dados.setdefault("subtopico_erro", "")
    with conectar() as conn:
        conn.execute(
            """INSERT INTO erros
               (id_bateria, materia, topico, subtopico_erro, qtd_erros,
                data, tipo_erro, status, usuario_id)
               VALUES (:id_bateria, :materia, :topico, :subtopico_erro, :qtd_erros,
                       :data, :tipo_erro, :status, :usuario_id)""",
            dados,
        )


def atualizar_status_erro(erro_id: int, novo_status: str, usuario_id: int):
    """Altera o status de um erro (pendente / revisado)."""
    with conectar() as conn:
        conn.execute(
            "UPDATE erros SET status = ? WHERE id = ? AND usuario_id = ?",
            (novo_status, erro_id, usuario_id),
        )


def ler_lancamentos(usuario_id: int) -> pd.DataFrame:
    """Retorna lancamentos do usuario como DataFrame."""
    with conectar() as conn:
        df = pd.read_sql_query(
            """SELECT id_bateria, materia, data, acertos, total,
                      fonte, subtopico, percentual
               FROM lancamentos WHERE usuario_id = ?""",
            conn, params=(usuario_id,),
        )
    df.rename(columns={
        "id_bateria": "ID Bateria", "materia": "Materia", "data": "Data",
        "acertos": "Acertos", "total": "Total", "fonte": "Fonte",
        "subtopico": "Subtopico", "percentual": "Percentual",
    }, inplace=True)
    df["Acertos"]    = pd.to_numeric(df["Acertos"],    errors="coerce").fillna(0).astype(int)
    df["Total"]      = pd.to_numeric(df["Total"],      errors="coerce").fillna(0).astype(int)
    df["Percentual"] = pd.to_numeric(df["Percentual"], errors="coerce").fillna(0)
    return df


def ler_erros(usuario_id: int) -> pd.DataFrame:
    """Retorna erros do usuario como DataFrame."""
    with conectar() as conn:
        df = pd.read_sql_query(
            """SELECT id, id_bateria, materia, topico, subtopico_erro,
                      qtd_erros, data, tipo_erro, status
               FROM erros WHERE usuario_id = ?""",
            conn, params=(usuario_id,),
        )
    df.rename(columns={
        "id": "ID", "id_bateria": "ID Bateria", "materia": "Materia",
        "topico": "Topico", "subtopico_erro": "Subtopico",
        "qtd_erros": "Qtd Erros", "data": "Data",
        "tipo_erro": "Tipo Erro", "status": "Status",
    }, inplace=True)
    df["Qtd Erros"] = pd.to_numeric(df["Qtd Erros"], errors="coerce").fillna(0).astype(int)
    df["Status"]    = df["Status"].fillna("pendente")
    df["Tipo Erro"] = df["Tipo Erro"].fillna("nao_sabia")
    df["Subtopico"] = df["Subtopico"].fillna("")
    return df


# ─── CADASTROS ────────────────────────────────────────────────────────────────

def get_materias_plano(usuario_id: int) -> list:
    """Retorna matérias do plano ativo do usuário (baseado na área de estudo).
    Usa a hierarquia canônica de config_materias.py."""
    from config_materias import MATERIAS_POR_AREA as _MAP
    with conectar() as conn:
        row = conn.execute(
            "SELECT area_estudo FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    area = (row["area_estudo"] or "outro") if row else "outro"
    return _MAP.get(area, _MAP["outro"])


def get_materias(usuario_id: int) -> list:
    """
    Retorna matérias disponíveis para o usuário.
    Combina o catálogo padrão com as matérias cadastradas manualmente,
    sem duplicatas, em ordem alfabética.
    """
    with conectar() as conn:
        rows = conn.execute(
            "SELECT DISTINCT materia FROM cadastros WHERE usuario_id = ? ORDER BY materia",
            (usuario_id,),
        ).fetchall()
    cadastradas = {r["materia"] for r in rows}
    todas = sorted(set(MATERIAS_PADRAO.keys()) | cadastradas)
    return todas


def get_assuntos(materia: str, usuario_id: int) -> list:
    """
    Retorna subtópicos de uma matéria.
    Combina o catálogo padrão com os assuntos cadastrados manualmente,
    sem duplicatas, em ordem alfabética.
    """
    with conectar() as conn:
        rows = conn.execute(
            """SELECT assunto FROM cadastros
               WHERE materia = ? AND assunto != '' AND usuario_id = ?
               ORDER BY assunto""",
            (materia, usuario_id),
        ).fetchall()
    cadastrados = {r["assunto"] for r in rows}
    padrao = set(MATERIAS_PADRAO.get(materia, []))
    return sorted(padrao | cadastrados)


def inserir_materia(materia: str, usuario_id: int):
    """Cria uma materia do usuario."""
    with conectar() as conn:
        conn.execute(
            "INSERT INTO cadastros (materia, assunto, usuario_id) VALUES (?, '', ?)",
            (materia, usuario_id),
        )


def inserir_assunto(materia: str, assunto: str, usuario_id: int):
    """Adiciona assunto a uma materia do usuario."""
    with conectar() as conn:
        conn.execute(
            "INSERT INTO cadastros (materia, assunto, usuario_id) VALUES (?, ?, ?)",
            (materia, assunto, usuario_id),
        )


def remover_assunto(materia: str, assunto: str, usuario_id: int):
    """Remove um assunto da materia do usuario."""
    with conectar() as conn:
        conn.execute(
            "DELETE FROM cadastros WHERE materia = ? AND assunto = ? AND usuario_id = ?",
            (materia, assunto, usuario_id),
        )


def remover_materia(materia: str, usuario_id: int):
    """Remove uma materia e todos os seus assuntos do usuario."""
    with conectar() as conn:
        conn.execute(
            "DELETE FROM cadastros WHERE materia = ? AND usuario_id = ?",
            (materia, usuario_id),
        )


def resetar_usuario(usuario_id: int):
    """Apaga todos os dados do usuario e retorna ao estado de novo usuario."""
    with conectar() as conn:
        conn.execute("DELETE FROM lancamentos WHERE usuario_id = ?", (usuario_id,))
        conn.execute("DELETE FROM erros       WHERE usuario_id = ?", (usuario_id,))
        conn.execute("DELETE FROM cadastros   WHERE usuario_id = ?", (usuario_id,))
        conn.execute("UPDATE usuarios SET plano = 'gratuito' WHERE id = ?", (usuario_id,))


def listar_usuarios_dev() -> list:
    """Retorna todos os usuários para o acesso rápido DEV na tela de login."""
    with conectar() as conn:
        rows = conn.execute(
            "SELECT id, nome, email, role FROM usuarios ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def gerar_dados_teste(usuario_id: int) -> dict:
    """
    Limpa os dados do usuário e gera dados de teste realistas:
    3 meses de baterias com mix de fontes, desempenhos variados e erros.
    Retorna {'baterias': N, 'lancamentos': N, 'erros': N}.
    """
    import random
    import json
    from datetime import date, timedelta

    MATERIAS = [
        ("Direito Administrativo",  [0.52, 0.65]),
        ("Direito Constitucional",  [0.75, 0.88]),
        ("Lingua Portuguesa",       [0.70, 0.82]),
        ("Raciocinio Logico",       [0.44, 0.58]),
        ("Legislacao Especifica",   [0.80, 0.92]),
        ("Conhecimentos Gerais",    [0.63, 0.78]),
    ]
    TOPICOS = {
        "Direito Administrativo": ["Atos Administrativos", "Licitacoes", "Processo Adm", "Poderes Adm", "Organizacao Adm"],
        "Direito Constitucional": ["Direitos Fundamentais", "Organizacao do Estado", "Poder Legislativo", "Controle de Constitucionalidade"],
        "Lingua Portuguesa":      ["Coerencia Textual", "Concordancia", "Regencia", "Pontuacao"],
        "Raciocinio Logico":      ["Proposicoes", "Conjuntos", "Sequencias Numericas", "Probabilidade"],
        "Legislacao Especifica":  ["Lei 8112", "Lei 8429", "Decreto 9094"],
        "Conhecimentos Gerais":   ["Atualidades", "Historia do Brasil", "Geografia"],
    }
    TIPOS_ERRO = ["nao_sabia", "confundiu", "esqueceu"]
    FONTES_W   = {"prova_mesma_banca": 0.15, "simulado": 0.25, "banco_questoes": 0.45, "ia_gerado": 0.15}

    hoje    = date.today()
    bat_num = 1
    random.seed(usuario_id * 7)

    with conectar() as conn:
        # Limpa dados existentes
        conn.execute("DELETE FROM lancamentos WHERE usuario_id = ?", (usuario_id,))
        conn.execute("DELETE FROM erros WHERE usuario_id = ?", (usuario_id,))
        # Ativa plano e configura plataformas
        conn.execute("UPDATE usuarios SET plano = 'ativo' WHERE id = ?", (usuario_id,))
        conn.execute(
            "UPDATE usuarios SET plataformas_ativas = ? WHERE id = ?",
            (json.dumps(["banco_questoes", "simulado", "ia_gerado"]), usuario_id),
        )

        for mes_offset in range(3, 0, -1):
            base = (hoje.replace(day=1) - timedelta(days=mes_offset * 31))
            for _ in range(random.randint(4, 6)):
                dia = random.randint(1, 28)
                try:    dt = base.replace(day=dia)
                except: dt = base.replace(day=28)

                bat_id   = f"B{bat_num:03d}"
                bat_num += 1
                fonte    = random.choices(list(FONTES_W.keys()), weights=list(FONTES_W.values()))[0]
                mats_bat = random.sample(MATERIAS, random.randint(2, 4))
                data_str = dt.strftime("%d/%m/%Y")

                for mat, (pmin, pmax) in mats_bat:
                    total   = random.choice([10, 15, 20])
                    acertos = max(0, min(round(total * random.uniform(pmin, pmax)), total))
                    conn.execute(
                        "INSERT INTO lancamentos (id_bateria,materia,data,acertos,total,fonte,subtopico,percentual,usuario_id) VALUES (?,?,?,?,?,?,?,?,?)",
                        (bat_id, mat, data_str, acertos, total, fonte, "", round(acertos/total*100, 1), usuario_id),
                    )
                    n_erros = total - acertos
                    if n_erros > 0:
                        tops = TOPICOS.get(mat, ["Topico Geral"])
                        for _ in range(min(n_erros, random.randint(1, 2))):
                            conn.execute(
                                "INSERT INTO erros (id_bateria,materia,topico,qtd_erros,data,tipo_erro,status,usuario_id) VALUES (?,?,?,?,?,?,?,?)",
                                (bat_id, mat, random.choice(tops), 1, data_str, random.choice(TIPOS_ERRO), "pendente", usuario_id),
                            )

        n_bat  = conn.execute("SELECT COUNT(DISTINCT id_bateria) FROM lancamentos WHERE usuario_id=?", (usuario_id,)).fetchone()[0]
        n_lanc = conn.execute("SELECT COUNT(*) FROM lancamentos WHERE usuario_id=?", (usuario_id,)).fetchone()[0]
        n_err  = conn.execute("SELECT COUNT(*) FROM erros WHERE usuario_id=?", (usuario_id,)).fetchone()[0]

    return {"baterias": n_bat, "lancamentos": n_lanc, "erros": n_err}


def copiar_dados_admin(usuario_id: int) -> int:
    """
    Copia todos os lancamentos, erros e cadastros do admin para o usuario_id.
    Os dados do admin nao sao alterados — apenas duplicados com novo usuario_id.
    Retorna o numero de lancamentos copiados.
    """
    with conectar() as conn:
        admin = conn.execute(
            "SELECT id FROM usuarios WHERE role = 'administrador' LIMIT 1"
        ).fetchone()
        if not admin:
            return 0
        admin_id = admin["id"]

        # Copia lancamentos (inclui legados com usuario_id NULL)
        conn.execute(
            """INSERT INTO lancamentos
               (id_bateria, materia, data, acertos, total, fonte, subtopico, percentual, usuario_id)
               SELECT id_bateria, materia, data, acertos, total, fonte, subtopico, percentual, ?
               FROM lancamentos WHERE usuario_id = ? OR usuario_id IS NULL""",
            (usuario_id, admin_id),
        )

        # Copia erros (inclui legados com usuario_id NULL)
        conn.execute(
            """INSERT INTO erros
               (id_bateria, materia, topico, qtd_erros, data, observacao, providencia, usuario_id)
               SELECT id_bateria, materia, topico, qtd_erros, data, observacao, providencia, ?
               FROM erros WHERE usuario_id = ? OR usuario_id IS NULL""",
            (usuario_id, admin_id),
        )

        # Copia cadastros (inclui legados com usuario_id NULL)
        conn.execute(
            """INSERT INTO cadastros (materia, assunto, usuario_id)
               SELECT materia, assunto, ?
               FROM cadastros WHERE usuario_id = ? OR usuario_id IS NULL""",
            (usuario_id, admin_id),
        )

        total = conn.execute(
            "SELECT COUNT(*) FROM lancamentos WHERE usuario_id = ?", (usuario_id,)
        ).fetchone()[0]
    return total
