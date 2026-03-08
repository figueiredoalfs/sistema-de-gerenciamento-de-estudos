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

# ─── CATÁLOGO PADRÃO ──────────────────────────────────────────────────────────
# Matérias e subtópicos mais cobrados em concursos públicos brasileiros.
# Exibidos para todos os usuários (não dependem de cadastro manual).

MATERIAS_PADRAO: dict[str, list[str]] = {
    "Português": [
        "Interpretação de Texto",
        "Concordância Verbal e Nominal",
        "Regência Verbal e Nominal",
        "Colocação Pronominal",
        "Pontuação",
        "Ortografia e Acentuação",
        "Semântica e Sinônimos",
        "Crase",
        "Figuras de Linguagem",
        "Redação Oficial",
    ],
    "Raciocínio Lógico": [
        "Proposições e Conectivos Lógicos",
        "Equivalências Lógicas",
        "Silogismo",
        "Diagramas Lógicos",
        "Sequências e Progressões",
        "Análise Combinatória",
        "Probabilidade",
        "Problemas de Contagem",
        "Conjuntos e Operações",
        "Lógica de Argumentação",
    ],
    "Matemática": [
        "Aritmética Básica",
        "Porcentagem",
        "Razão e Proporção",
        "Regra de Três",
        "Operações com Frações",
        "Geometria Plana",
        "Álgebra e Equações",
        "Progressões (PA e PG)",
        "Estatística Básica",
        "Conjuntos",
    ],
    "Matemática Financeira": [
        "Juros Simples",
        "Juros Compostos",
        "Descontos",
        "Séries de Pagamentos",
        "Amortização",
        "Equivalência de Capitais",
        "VPL e TIR",
        "Fluxo de Caixa",
    ],
    "Direito Constitucional": [
        "Princípios Fundamentais",
        "Direitos e Garantias Fundamentais",
        "Remédios Constitucionais",
        "Organização do Estado",
        "Poder Legislativo",
        "Poder Executivo",
        "Poder Judiciário",
        "Controle de Constitucionalidade",
        "Processo Legislativo",
        "Ordem Econômica e Social",
    ],
    "Direito Administrativo": [
        "Princípios da Administração Pública",
        "Atos Administrativos",
        "Licitações (Lei 14.133/2021)",
        "Contratos Administrativos",
        "Servidores Públicos (Lei 8.112/1990)",
        "Responsabilidade Civil do Estado",
        "Processo Administrativo",
        "Poderes Administrativos",
        "Bens Públicos",
        "Controle da Administração",
        "Improbidade Administrativa",
    ],
    "Direito Penal": [
        "Parte Geral — Tipicidade e Culpabilidade",
        "Teoria da Pena",
        "Excludentes de Ilicitude",
        "Crimes contra a Pessoa",
        "Crimes contra o Patrimônio",
        "Crimes contra a Fé Pública",
        "Crimes contra a Administração Pública",
        "Lei de Drogas",
        "Circunstâncias Agravantes e Atenuantes",
        "Extinção da Punibilidade",
    ],
    "Direito Processual Penal": [
        "Inquérito Policial",
        "Ação Penal",
        "Prisão em Flagrante",
        "Prisão Preventiva e Temporária",
        "Medidas Cautelares",
        "Prova Penal",
        "Competência Jurisdicional",
        "Habeas Corpus",
        "Recursos",
        "Júri",
    ],
    "Direito Civil": [
        "Parte Geral",
        "Obrigações",
        "Contratos em Espécie",
        "Responsabilidade Civil",
        "Direito de Família",
        "Direito das Coisas",
        "Sucessões",
        "Posse e Propriedade",
    ],
    "Direito Processual Civil": [
        "Princípios",
        "Competência",
        "Processo de Conhecimento",
        "Tutelas Provisórias",
        "Provas",
        "Sentença e Coisa Julgada",
        "Recursos",
        "Execução",
        "Procedimentos Especiais",
    ],
    "Direito Tributário": [
        "Sistema Tributário Nacional",
        "Princípios Constitucionais Tributários",
        "Espécies de Tributos",
        "Obrigação Tributária",
        "Crédito Tributário",
        "Lançamento Tributário",
        "Extinção da Obrigação Tributária",
        "Exclusão do Crédito Tributário",
        "Responsabilidade Tributária",
        "Processo Tributário",
        "CTN (Lei 5.172/1966)",
    ],
    "Contabilidade": [
        "Balanço Patrimonial",
        "Demonstração de Resultado (DRE)",
        "Escrituração",
        "Patrimônio Líquido",
        "Depreciação e Amortização",
        "Análise das Demonstrações",
        "Contabilidade de Custos",
        "Contabilidade Pública",
        "Auditoria",
        "Normas Brasileiras de Contabilidade",
    ],
    "Administração": [
        "Teorias Administrativas",
        "Planejamento, Organização, Direção e Controle",
        "Gestão de Pessoas",
        "Gestão por Competências",
        "Liderança e Motivação",
        "Cultura Organizacional",
        "Gestão Estratégica",
        "Gestão de Projetos",
        "Qualidade e Produtividade",
        "Gestão por Processos",
    ],
    "Informática": [
        "Word (Microsoft / LibreOffice)",
        "Excel — Fórmulas e Funções",
        "PowerPoint",
        "Internet e Navegadores",
        "E-mail e Comunicação Digital",
        "Sistemas Operacionais (Windows / Linux)",
        "Hardware Básico",
        "Nuvem (OneDrive, Google Drive)",
        "Segurança Digital e Antivírus",
        "Backup e Recuperação",
    ],
    "Segurança da Informação": [
        "Criptografia",
        "Vírus, Malware e Ransomware",
        "Firewall e IDS/IPS",
        "Autenticação e Controle de Acesso",
        "Phishing e Engenharia Social",
        "Certificados Digitais",
        "LGPD (Lei 13.709/2018)",
        "Protocolos de Segurança (HTTPS, SSL/TLS)",
        "ISO 27001",
        "Gestão de Riscos",
    ],
    "Redes de Computadores": [
        "Modelos OSI e TCP/IP",
        "Endereçamento IP (IPv4 e IPv6)",
        "Subredes e Máscara de Rede",
        "Protocolos (HTTP, FTP, SMTP, DNS)",
        "Roteamento",
        "Switches e VLANs",
        "Topologias de Rede",
        "Wi-Fi e Cabeamento",
        "VPN",
        "Monitoramento de Rede",
    ],
    "Banco de Dados": [
        "Modelo Relacional",
        "SQL — SELECT e Filtros",
        "SQL — JOIN, GROUP BY, HAVING",
        "SQL — INSERT, UPDATE, DELETE",
        "Normalização (1FN, 2FN, 3FN)",
        "Índices e Otimização",
        "Transações e ACID",
        "Triggers e Procedures",
        "NoSQL (MongoDB, Redis)",
        "Backup e Recuperação",
    ],
    "Governança de TI": [
        "ITIL — Conceitos e Processos",
        "COBIT",
        "Gerenciamento de Incidentes",
        "Gerenciamento de Mudanças",
        "SLA e Gestão de Nível de Serviço",
        "Continuidade de Negócios",
        "Disaster Recovery",
        "ISO 20000",
        "Gestão de Capacidade",
        "Gestão de Configuração",
    ],
    "Legislação do SUS": [
        "Lei 8.080/1990 — Lei Orgânica da Saúde",
        "Lei 8.142/1990 — Participação Social",
        "Decreto 7.508/2011",
        "Princípios do SUS (Universalidade, Equidade, Integralidade)",
        "Diretrizes do SUS",
        "Organização e Gestão do SUS",
        "Financiamento do SUS",
        "Conselhos e Conferências de Saúde",
        "NOB e NOAS",
        "Pacto pela Saúde",
    ],
    "Saúde Pública": [
        "Epidemiologia Básica",
        "Indicadores de Saúde",
        "Vigilância em Saúde",
        "Doenças de Notificação Obrigatória",
        "Promoção da Saúde",
        "Prevenção de Doenças",
        "Determinantes Sociais da Saúde",
        "Surtos e Epidemias",
        "Saúde da Família (ESF)",
        "Atenção Primária à Saúde",
    ],
    "Atualidades": [
        "Política Nacional",
        "Política Internacional",
        "Economia Brasileira",
        "Meio Ambiente e Clima",
        "Ciência e Tecnologia",
        "Direitos Humanos",
        "Saúde e Pandemia",
        "Segurança Pública",
        "Educação",
        "Questões Sociais",
    ],
    "Legislação Específica": [
        "Lei Orgânica do Órgão",
        "Regimento Interno",
        "Estatuto do Servidor",
        "Código de Ética",
        "Legislação Ambiental",
        "Leis Complementares",
    ],
}


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
    with conectar() as conn:
        conn.execute(
            """INSERT INTO erros
               (id_bateria, materia, topico, qtd_erros, data, observacao, providencia, usuario_id)
               VALUES (:id_bateria, :materia, :topico, :qtd_erros,
                       :data, :observacao, :providencia, :usuario_id)""",
            dados,
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
            """SELECT id_bateria, materia, topico, qtd_erros,
                      data, observacao, providencia
               FROM erros WHERE usuario_id = ?""",
            conn, params=(usuario_id,),
        )
    df.rename(columns={
        "id_bateria": "ID Bateria", "materia": "Materia", "topico": "Topico",
        "qtd_erros": "Qtd Erros", "data": "Data",
        "observacao": "Observacao", "providencia": "Providencia",
    }, inplace=True)
    df["Qtd Erros"] = pd.to_numeric(df["Qtd Erros"], errors="coerce").fillna(0).astype(int)
    return df


# ─── CADASTROS ────────────────────────────────────────────────────────────────

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
