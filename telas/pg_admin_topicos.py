"""
telas/pg_admin_topicos.py
CRUD de tópicos: matéria (nivel 0), bloco (nivel 1), tópico (nivel 2).
"""

import requests
import streamlit as st

_API_BASE = "http://localhost:8000"

NIVEL_LABEL = {0: "Matéria", 1: "Bloco", 2: "Tópico"}
AREAS = ["Fiscal", "Jurídica", "Policial", "TI", "Saúde", "Outro"]


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _listar(nivel: int = None, parent_id: str = None, apenas_ativos: bool = True) -> list:
    params = {"apenas_ativos": apenas_ativos}
    if nivel is not None:
        params["nivel"] = nivel
    if parent_id:
        params["parent_id"] = parent_id
    try:
        r = requests.get(f"{_API_BASE}/admin/topicos", params=params, headers=_headers(), timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def _criar(dados: dict) -> dict | None:
    try:
        r = requests.post(f"{_API_BASE}/admin/topicos", json=dados, headers=_headers(), timeout=8)
        if r.status_code == 201:
            return r.json()
        st.error(f"Erro {r.status_code}: {r.json().get('detail', 'Erro desconhecido')}")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
    return None


def _editar(topico_id: str, dados: dict) -> dict | None:
    try:
        r = requests.patch(f"{_API_BASE}/admin/topicos/{topico_id}", json=dados, headers=_headers(), timeout=8)
        if r.status_code == 200:
            return r.json()
        st.error(f"Erro {r.status_code}: {r.json().get('detail', 'Erro desconhecido')}")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
    return None


def _desativar(topico_id: str) -> bool:
    try:
        r = requests.delete(f"{_API_BASE}/admin/topicos/{topico_id}", headers=_headers(), timeout=8)
        return r.status_code == 204
    except Exception:
        return False


def _form_criar(nivel: int, materias: list, blocos: list):
    """Formulário de criação de tópico."""
    with st.form(key=f"form_criar_{nivel}", clear_on_submit=True):
        st.markdown(f"##### Criar {NIVEL_LABEL[nivel]}")
        nome = st.text_input("Nome *", key=f"criar_nome_{nivel}")

        parent_id = None
        if nivel == 1:
            mat_opts  = {m["nome"]: m["id"] for m in materias}
            mat_sel   = st.selectbox("Matéria pai *", ["(selecione)"] + list(mat_opts.keys()), key=f"criar_pai_b")
            parent_id = mat_opts.get(mat_sel)
        elif nivel == 2:
            bloco_opts = {b["nome"]: b["id"] for b in blocos}
            bloco_sel  = st.selectbox("Bloco pai *", ["(selecione)"] + list(bloco_opts.keys()), key=f"criar_pai_t")
            parent_id  = bloco_opts.get(bloco_sel)

        col1, col2 = st.columns(2)
        with col1:
            area   = st.selectbox("Área", [""] + AREAS, key=f"criar_area_{nivel}")
            peso   = st.number_input("Peso edital", min_value=0.1, max_value=5.0, value=1.0, step=0.1,
                                     key=f"criar_peso_{nivel}")
        with col2:
            banca  = st.text_input("Banca (opcional)", key=f"criar_banca_{nivel}")
            decay  = st.number_input("Decay rate", min_value=0.01, max_value=0.3, value=0.05, step=0.01,
                                     key=f"criar_decay_{nivel}")
        descricao = st.text_area("Descrição (opcional)", height=60, key=f"criar_desc_{nivel}")

        if st.form_submit_button(f"Criar {NIVEL_LABEL[nivel]}", type="primary"):
            if not nome.strip():
                st.warning("Nome é obrigatório.")
            elif nivel > 0 and not parent_id:
                st.warning("Selecione o pai.")
            else:
                ok = _criar({
                    "nome": nome.strip(),
                    "nivel": nivel,
                    "parent_id": parent_id,
                    "area": area or None,
                    "banca": banca.strip() or None,
                    "descricao": descricao.strip() or None,
                    "peso_edital": peso,
                    "decay_rate": decay,
                    "dependencias_json": "[]",
                })
                if ok:
                    st.success(f"{NIVEL_LABEL[nivel]} '{ok['nome']}' criado.")
                    st.rerun()


def render():
    st.markdown("## Gerenciar Tópicos")
    st.caption("Matérias, blocos e tópicos usados no planejamento de estudo.")

    aba_mat, aba_bloco, aba_top = st.tabs(["Matérias (Nível 0)", "Blocos (Nível 1)", "Tópicos (Nível 2)"])

    # ── ABA MATÉRIAS ──────────────────────────────────────────────────────────
    with aba_mat:
        materias = _listar(nivel=0, apenas_ativos=False)

        col_list, col_form = st.columns([3, 2])

        with col_list:
            st.markdown("#### Lista de matérias")
            if not materias:
                st.info("Nenhuma matéria cadastrada.")
            else:
                for mat in materias:
                    cor_status = "#4ade80" if mat["ativo"] else "#e74c3c"
                    with st.expander(f"{mat['nome']} — {mat.get('area') or '—'}", expanded=False):
                        st.markdown(
                            f"**ID:** `{mat['id'][:8]}…`  |  "
                            f"**Área:** {mat.get('area') or '—'}  |  "
                            f"**Peso:** {mat['peso_edital']}  |  "
                            f"**Status:** <span style='color:{cor_status};font-weight:700;'>"
                            f"{'Ativo' if mat['ativo'] else 'Inativo'}</span>",
                            unsafe_allow_html=True,
                        )
                        c1, c2 = st.columns(2)
                        novo_nome = c1.text_input("Novo nome", value=mat["nome"], key=f"edit_mat_{mat['id']}")
                        novo_peso = c2.number_input("Peso", min_value=0.1, max_value=5.0, value=float(mat["peso_edital"]),
                                                    step=0.1, key=f"peso_mat_{mat['id']}")
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.button("Salvar", key=f"salvar_mat_{mat['id']}", use_container_width=True):
                            ok = _editar(mat["id"], {"nome": novo_nome.strip(), "peso_edital": novo_peso})
                            if ok:
                                st.success("Matéria atualizada.")
                                st.rerun()
                        if mat["ativo"]:
                            if col_btn2.button("Desativar", key=f"del_mat_{mat['id']}", use_container_width=True):
                                if _desativar(mat["id"]):
                                    st.success("Matéria desativada.")
                                    st.rerun()

        with col_form:
            _form_criar(nivel=0, materias=[], blocos=[])

    # ── ABA BLOCOS ────────────────────────────────────────────────────────────
    with aba_bloco:
        materias_ativas = _listar(nivel=0)
        blocos = _listar(nivel=1, apenas_ativos=False)

        col_list, col_form = st.columns([3, 2])

        with col_list:
            st.markdown("#### Lista de blocos")

            mat_filtro_opts = {m["nome"]: m["id"] for m in materias_ativas}
            mat_filtro = st.selectbox("Filtrar por matéria", ["Todas"] + list(mat_filtro_opts.keys()),
                                      key="filtro_bloco_mat")
            blocos_exib = blocos
            if mat_filtro != "Todas":
                pid = mat_filtro_opts[mat_filtro]
                blocos_exib = [b for b in blocos if b.get("parent_id") == pid]

            if not blocos_exib:
                st.info("Nenhum bloco encontrado.")
            else:
                for bloco in blocos_exib:
                    cor_status = "#4ade80" if bloco["ativo"] else "#e74c3c"
                    mat_nome = next((m["nome"] for m in materias_ativas if m["id"] == bloco.get("parent_id")), "—")
                    with st.expander(f"{bloco['nome']} ({mat_nome})", expanded=False):
                        st.markdown(
                            f"**Matéria:** {mat_nome}  |  "
                            f"**Status:** <span style='color:{cor_status};font-weight:700;'>"
                            f"{'Ativo' if bloco['ativo'] else 'Inativo'}</span>",
                            unsafe_allow_html=True,
                        )
                        novo_nome = st.text_input("Novo nome", value=bloco["nome"], key=f"edit_bloco_{bloco['id']}")
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.button("Salvar", key=f"salvar_bloco_{bloco['id']}", use_container_width=True):
                            ok = _editar(bloco["id"], {"nome": novo_nome.strip()})
                            if ok:
                                st.success("Bloco atualizado.")
                                st.rerun()
                        if bloco["ativo"]:
                            if col_btn2.button("Desativar", key=f"del_bloco_{bloco['id']}", use_container_width=True):
                                if _desativar(bloco["id"]):
                                    st.success("Bloco desativado.")
                                    st.rerun()

        with col_form:
            _form_criar(nivel=1, materias=materias_ativas, blocos=[])

    # ── ABA TÓPICOS ───────────────────────────────────────────────────────────
    with aba_top:
        materias_ativas = _listar(nivel=0)
        blocos_ativos   = _listar(nivel=1)

        # Filtro de matéria para reduzir blocos
        mat_opts = {m["nome"]: m["id"] for m in materias_ativas}
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            mat_sel_top = st.selectbox("Matéria", ["Todas"] + list(mat_opts.keys()), key="top_mat_sel")
        blocos_exib = blocos_ativos
        if mat_sel_top != "Todas":
            pid_mat = mat_opts[mat_sel_top]
            blocos_exib = [b for b in blocos_ativos if b.get("parent_id") == pid_mat]

        bloco_opts = {b["nome"]: b["id"] for b in blocos_exib}
        with col_f2:
            bloco_sel_top = st.selectbox("Bloco", ["Todos"] + list(bloco_opts.keys()), key="top_bloco_sel")

        # Carrega tópicos
        pid_bloco = bloco_opts.get(bloco_sel_top) if bloco_sel_top != "Todos" else None
        topicos = _listar(nivel=2, parent_id=pid_bloco, apenas_ativos=False)

        col_list, col_form = st.columns([3, 2])

        with col_list:
            st.markdown(f"#### {len(topicos)} tópico(s)")
            if not topicos:
                st.info("Nenhum tópico encontrado.")
            else:
                for top in topicos:
                    cor_status = "#4ade80" if top["ativo"] else "#e74c3c"
                    bloco_nome = next((b["nome"] for b in blocos_ativos if b["id"] == top.get("parent_id")), "—")
                    with st.expander(f"{top['nome']}", expanded=False):
                        st.markdown(
                            f"**Bloco:** {bloco_nome}  |  "
                            f"**Peso:** {top['peso_edital']}  |  "
                            f"**Status:** <span style='color:{cor_status};font-weight:700;'>"
                            f"{'Ativo' if top['ativo'] else 'Inativo'}</span>",
                            unsafe_allow_html=True,
                        )
                        c1, c2 = st.columns(2)
                        novo_nome = c1.text_input("Nome", value=top["nome"], key=f"edit_top_{top['id']}")
                        novo_peso = c2.number_input("Peso", min_value=0.1, max_value=5.0, value=float(top["peso_edital"]),
                                                    step=0.1, key=f"peso_top_{top['id']}")
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.button("Salvar", key=f"salvar_top_{top['id']}", use_container_width=True):
                            ok = _editar(top["id"], {"nome": novo_nome.strip(), "peso_edital": novo_peso})
                            if ok:
                                st.success("Tópico atualizado.")
                                st.rerun()
                        if top["ativo"]:
                            if col_btn2.button("Desativar", key=f"del_top_{top['id']}", use_container_width=True):
                                if _desativar(top["id"]):
                                    st.success("Tópico desativado.")
                                    st.rerun()

        with col_form:
            _form_criar(nivel=2, materias=materias_ativas, blocos=blocos_exib)
