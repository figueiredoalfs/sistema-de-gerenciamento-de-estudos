"""
telas/pg_admin_importar_questoes.py — Tela de importação e classificação de questões.
"""

import csv
import io
import json

import requests
import streamlit as st

_API_BASE = "http://localhost:8000"


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


# ─── Parsers ──────────────────────────────────────────────────────────────────

def _parse_json(conteudo: bytes) -> tuple[list, str | None]:
    try:
        dados = json.loads(conteudo.decode("utf-8"))
        if not isinstance(dados, list):
            return [], "O arquivo JSON deve conter um array de questões no nível raiz."
        return dados, None
    except json.JSONDecodeError as exc:
        return [], f"JSON inválido: {exc}"


def _parse_csv(conteudo: bytes) -> tuple[list, str | None]:
    try:
        texto = conteudo.decode("utf-8")
        reader = csv.DictReader(io.StringIO(texto))
        questoes = []
        for row in reader:
            questoes.append({
                "subject": row.get("subject", ""),
                "board": row.get("board") or None,
                "year": int(row["year"]) if row.get("year") else None,
                "statement": row.get("statement", ""),
                "alternatives": {
                    "A": row.get("alternatives_A", ""),
                    "B": row.get("alternatives_B", ""),
                    "C": row.get("alternatives_C", ""),
                    "D": row.get("alternatives_D", ""),
                    "E": row.get("alternatives_E", ""),
                },
                "correct_answer": row.get("correct_answer", "").strip().upper(),
            })
        return questoes, None
    except Exception as exc:
        return [], f"Erro ao ler CSV: {exc}"


def _validar_questoes(questoes: list) -> list[str]:
    erros = []
    campos_obrigatorios = {"subject", "statement", "alternatives", "correct_answer"}
    alternativas_validas = {"A", "B", "C", "D", "E"}

    for i, q in enumerate(questoes, start=1):
        faltando = campos_obrigatorios - set(q.keys())
        if faltando:
            erros.append(f"Questão {i}: campos obrigatórios ausentes — {faltando}")
            continue

        if q.get("correct_answer", "").upper() not in alternativas_validas:
            erros.append(f"Questão {i}: correct_answer deve ser A, B, C, D ou E.")

        alts = q.get("alternatives", {})
        faltando_alts = {"A", "B", "C", "D", "E"} - set(alts.keys())
        if faltando_alts:
            erros.append(f"Questão {i}: alternativas ausentes — {faltando_alts}")

    return erros


# ─── Chamadas de API — importação ─────────────────────────────────────────────

def _importar(disciplina_sigla: str, questoes: list) -> dict:
    payload = {"disciplina_sigla": disciplina_sigla, "questoes": questoes}
    try:
        r = requests.post(
            f"{_API_BASE}/admin/importar-questoes",
            json=payload,
            headers=_headers(),
            timeout=30,
        )
        if r.status_code == 201:
            return r.json()
        return {"importadas": 0, "erros": [r.json().get("detail", "Erro desconhecido")]}
    except Exception as exc:
        return {"importadas": 0, "erros": [str(exc)]}


def _fetch_historico(subject="", board="", year=None, sigla="") -> list:
    params = {}
    if subject:
        params["subject"] = subject
    if board:
        params["board"] = board
    if year:
        params["year"] = year
    if sigla:
        params["disciplina_sigla"] = sigla
    try:
        r = requests.get(
            f"{_API_BASE}/admin/questoes-banco",
            params=params,
            headers=_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


# ─── Chamadas de API — subtópicos ─────────────────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def _fetch_topicos_nivel2(token: str) -> list:
    """Carrega todos os subtópicos (nivel=2) ativos. Cache de 2 minutos."""
    try:
        r = requests.get(
            f"{_API_BASE}/admin/topicos",
            params={"nivel": 2, "apenas_ativos": "true"},
            headers={"Authorization": f"Bearer {token}"} if token else {},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def _fetch_subtopicos_questao(question_id: str) -> list:
    try:
        r = requests.get(
            f"{_API_BASE}/admin/questoes-banco/{question_id}/subtopicos",
            headers=_headers(),
            timeout=5,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def _associar_subtopicos(question_id: str, subtopic_ids: list) -> tuple[list, str | None]:
    try:
        r = requests.post(
            f"{_API_BASE}/admin/questoes-banco/{question_id}/subtopicos",
            json={"subtopic_ids": subtopic_ids},
            headers=_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            return r.json(), None
        return [], r.json().get("detail", "Erro ao associar")
    except Exception as exc:
        return [], str(exc)


def _remover_subtopico(question_id: str, subtopic_id: str) -> str | None:
    try:
        r = requests.delete(
            f"{_API_BASE}/admin/questoes-banco/{question_id}/subtopicos/{subtopic_id}",
            headers=_headers(),
            timeout=5,
        )
        if r.status_code == 204:
            return None
        return r.json().get("detail", "Erro ao remover")
    except Exception as exc:
        return str(exc)


# ─── Sub-componente: painel de subtópicos por questão ─────────────────────────

def _painel_subtopicos(question_id: str, question_code: str, todos_nivel2: list):
    """Renderiza o expander de subtópicos para uma questão."""
    subtopicos_atuais = _fetch_subtopicos_questao(question_id)
    ids_atuais = {s["id"] for s in subtopicos_atuais}

    with st.expander(f"🏷️  {question_code} — subtópicos ({len(subtopicos_atuais)} associado(s))"):

        # Subtópicos já associados
        if subtopicos_atuais:
            st.markdown("**Associados:**")
            for sub in subtopicos_atuais:
                col_nome, col_btn = st.columns([5, 1])
                col_nome.markdown(
                    f'<span style="font-size:.85rem;color:#c8dff0;">{sub["nome"]}</span>',
                    unsafe_allow_html=True,
                )
                if col_btn.button("✕", key=f"rm_{question_id}_{sub['id']}", help="Remover"):
                    erro = _remover_subtopico(question_id, sub["id"])
                    if erro:
                        st.error(erro)
                    else:
                        st.toast(f"Subtópico '{sub['nome']}' removido.")
                        st.rerun()
        else:
            st.markdown(
                '<span style="color:#4a6a8a;font-size:.83rem;">Nenhum subtópico associado.</span>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Seletor para adicionar novos
        opcoes_disponiveis = [t for t in todos_nivel2 if t["id"] not in ids_atuais]

        if opcoes_disponiveis:
            opcoes_map = {t["id"]: t["nome"] for t in opcoes_disponiveis}
            selecionados = st.multiselect(
                "Adicionar subtópicos",
                options=list(opcoes_map.keys()),
                format_func=lambda x: opcoes_map[x],
                key=f"ms_{question_id}",
                placeholder="Selecione um ou mais subtópicos...",
            )

            if st.button("➕ Salvar", key=f"save_{question_id}", type="primary"):
                if selecionados:
                    _, erro = _associar_subtopicos(question_id, selecionados)
                    if erro:
                        st.error(erro)
                    else:
                        st.toast(f"{len(selecionados)} subtópico(s) associado(s).")
                        st.rerun()
                else:
                    st.info("Selecione ao menos um subtópico.")
        else:
            st.markdown(
                '<span style="color:#4a6a8a;font-size:.83rem;">Todos os subtópicos disponíveis já estão associados.</span>',
                unsafe_allow_html=True,
            )


# ─── Render principal ─────────────────────────────────────────────────────────

def render():
    if st.session_state.get("usuario", {}).get("role") != "administrador":
        st.error("Acesso negado. Esta área é restrita a administradores.")
        st.stop()

    st.markdown(
        '<h2 style="margin-bottom:4px;">📥 Importar Questões</h2>'
        '<p style="color:#4a6a8a;font-size:.87rem;margin-bottom:24px;">'
        'Importe questões em lote via arquivo JSON ou CSV gerado externamente.</p>',
        unsafe_allow_html=True,
    )

    aba_import, aba_historico = st.tabs(["📤 Importar", "📋 Histórico & Subtópicos"])

    # ── Aba: Importar ─────────────────────────────────────────────────────────
    with aba_import:
        st.markdown("#### Configuração da importação")

        col1, col2 = st.columns([1, 2])
        with col1:
            disciplina_sigla = st.text_input(
                "Sigla da disciplina",
                placeholder="Ex: DTRIB",
                help="Prefixo usado no código da questão (ex: DTRIB-FGV-2021-0001)",
            ).strip().upper()

        with col2:
            arquivo = st.file_uploader(
                "Arquivo de questões",
                type=["json", "csv"],
                help="JSON (array de objetos) ou CSV com colunas: subject, board, year, statement, alternatives_A..E, correct_answer",
            )

        if arquivo and disciplina_sigla:
            conteudo = arquivo.read()
            ext = arquivo.name.rsplit(".", 1)[-1].lower()

            questoes_raw, erro_parse = _parse_json(conteudo) if ext == "json" else _parse_csv(conteudo)

            if erro_parse:
                st.error(f"Erro ao ler arquivo: {erro_parse}")
                st.stop()

            erros_validacao = _validar_questoes(questoes_raw)
            if erros_validacao:
                st.warning(f"{len(erros_validacao)} problema(s) encontrado(s) no arquivo:")
                for e in erros_validacao[:10]:
                    st.markdown(f"- {e}")
                if len(erros_validacao) > 10:
                    st.markdown(f"_...e mais {len(erros_validacao) - 10} erros._")
                st.stop()

            st.markdown(f"#### Pré-visualização — {len(questoes_raw)} questão(ões) encontrada(s)")

            col_h1, col_h2, col_h3, col_h4 = st.columns([3, 1, 1, 1])
            col_h1.markdown("**Enunciado**")
            col_h2.markdown("**Disciplina**")
            col_h3.markdown("**Banca / Ano**")
            col_h4.markdown("**Gabarito**")
            st.markdown('<hr style="margin:4px 0 8px 0;border-color:#1a3a55;">', unsafe_allow_html=True)

            for q in questoes_raw[:20]:
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                enunciado_curto = (q.get("statement") or "")[:80]
                if len(q.get("statement", "")) > 80:
                    enunciado_curto += "…"
                c1.markdown(f'<span style="font-size:.85rem;">{enunciado_curto}</span>', unsafe_allow_html=True)
                c2.markdown(f'<span style="color:#7a9ab8;font-size:.85rem;">{q.get("subject","")[:20]}</span>', unsafe_allow_html=True)
                banca_ano = f"{q.get('board','') or '—'} / {q.get('year','') or '—'}"
                c3.markdown(f'<span style="color:#7a9ab8;font-size:.85rem;">{banca_ano}</span>', unsafe_allow_html=True)
                c4.markdown(
                    f'<span style="background:#1a3a55;padding:2px 8px;border-radius:4px;font-size:.85rem;">'
                    f'{q.get("correct_answer","")}</span>',
                    unsafe_allow_html=True,
                )

            if len(questoes_raw) > 20:
                st.info(f"Mostrando as primeiras 20 de {len(questoes_raw)} questões.")

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✅ Confirmar Importação", type="primary"):
                for q in questoes_raw:
                    if "correct_answer" in q:
                        q["correct_answer"] = q["correct_answer"].strip().upper()

                with st.spinner("Importando questões..."):
                    resultado = _importar(disciplina_sigla, questoes_raw)

                importadas = resultado.get("importadas", 0)
                erros_api = resultado.get("erros", [])

                if importadas > 0:
                    st.success(f"{importadas} questão(ões) importada(s) com sucesso!")
                    st.toast(f"✅ {importadas} questões importadas")

                if erros_api:
                    st.warning(f"{len(erros_api)} erro(s) durante a importação:")
                    for e in erros_api:
                        st.markdown(f"- {e}")

        elif arquivo and not disciplina_sigla:
            st.info("Informe a sigla da disciplina para prosseguir.")
        else:
            st.markdown(
                '<div style="background:#0f1e2e;border:1px solid #1a3a55;border-radius:10px;padding:20px 24px;">'
                '<p style="color:#5a7a96;margin:0 0 12px 0;font-weight:600;">Formato JSON esperado:</p>'
                '<pre style="background:#050d14;padding:12px;border-radius:6px;font-size:.78rem;color:#c8dff0;">'
                '[\n'
                '  {\n'
                '    "subject": "Direito Tributário",\n'
                '    "board": "FGV",\n'
                '    "year": 2021,\n'
                '    "statement": "Texto da questão...",\n'
                '    "alternatives": {\n'
                '      "A": "Primeira alternativa",\n'
                '      "B": "Segunda alternativa",\n'
                '      "C": "Terceira alternativa",\n'
                '      "D": "Quarta alternativa",\n'
                '      "E": "Quinta alternativa"\n'
                '    },\n'
                '    "correct_answer": "B"\n'
                '  }\n'
                ']'
                '</pre>'
                '<p style="color:#5a7a96;margin:12px 0 4px 0;font-weight:600;">Colunas CSV esperadas:</p>'
                '<code style="color:#c8dff0;font-size:.78rem;">'
                'subject, board, year, statement, alternatives_A, alternatives_B, alternatives_C, alternatives_D, alternatives_E, correct_answer'
                '</code>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── Aba: Histórico & Subtópicos ───────────────────────────────────────────
    with aba_historico:
        st.markdown("#### Questões importadas")

        cf1, cf2, cf3, cf4 = st.columns([2, 1, 1, 1])
        with cf1:
            f_subject = st.text_input("Disciplina", placeholder="Direito Tributário", key="hist_subject")
        with cf2:
            f_board = st.text_input("Banca", placeholder="FGV", key="hist_board")
        with cf3:
            f_year = st.number_input("Ano", min_value=2000, max_value=2030, value=None, step=1, key="hist_year", format="%d")
        with cf4:
            f_sigla = st.text_input("Sigla", placeholder="DTRIB", key="hist_sigla").strip().upper()

        questoes = _fetch_historico(f_subject, f_board, f_year, f_sigla)

        # Carrega subtópicos nível 2 uma única vez (com cache)
        token = st.session_state.get("api_token", "")
        todos_nivel2 = _fetch_topicos_nivel2(token)

        if not questoes:
            st.info("Nenhuma questão encontrada. Ajuste os filtros ou importe questões na aba anterior.")
        else:
            st.markdown(f"**{len(questoes)} questão(ões) encontrada(s)**")
            st.markdown('<hr style="margin:4px 0 8px 0;border-color:#1a3a55;">', unsafe_allow_html=True)

            h1, h2, h3, h4, h5 = st.columns([1.5, 2, 3, 1, 1])
            h1.markdown("**Código**")
            h2.markdown("**Disciplina**")
            h3.markdown("**Enunciado**")
            h4.markdown("**Banca/Ano**")
            h5.markdown("**Gabarito**")
            st.markdown('<hr style="margin:2px 0 4px 0;border-color:#1a3a55;">', unsafe_allow_html=True)

            for q in questoes:
                c1, c2, c3, c4, c5 = st.columns([1.5, 2, 3, 1, 1])
                c1.markdown(
                    f'<span style="color:#3a86ff;font-size:.78rem;">{q.get("question_code","")}</span>',
                    unsafe_allow_html=True,
                )
                c2.markdown(
                    f'<span style="font-size:.82rem;">{q.get("subject","")[:30]}</span>',
                    unsafe_allow_html=True,
                )
                enunciado = (q.get("statement") or "")[:70]
                if len(q.get("statement", "")) > 70:
                    enunciado += "…"
                c3.markdown(
                    f'<span style="color:#7a9ab8;font-size:.82rem;">{enunciado}</span>',
                    unsafe_allow_html=True,
                )
                c4.markdown(
                    f'<span style="color:#7a9ab8;font-size:.82rem;">{q.get("board","—")} / {q.get("year","—")}</span>',
                    unsafe_allow_html=True,
                )
                c5.markdown(
                    f'<span style="background:#1a3a55;padding:2px 8px;border-radius:4px;font-size:.82rem;">'
                    f'{q.get("correct_answer","")}</span>',
                    unsafe_allow_html=True,
                )

                # Expander de subtópicos abaixo de cada linha
                _painel_subtopicos(q["id"], q["question_code"], todos_nivel2)
                st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
