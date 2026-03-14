"""
telas/pg_admin_usuarios.py — Listagem de alunos cadastrados.
"""

import requests
import streamlit as st

_API_BASE = "http://localhost:8000"


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _listar_alunos() -> list:
    try:
        r = requests.get(f"{_API_BASE}/admin/alunos", headers=_headers(), timeout=5)
        if r.status_code == 200:
            return r.json().get("itens", [])
    except Exception:
        pass
    return []


def render():
    if st.session_state.get("usuario", {}).get("role") != "administrador":
        st.error("Acesso negado.")
        st.stop()

    st.markdown("## 👥 Usuários Cadastrados")
    st.caption("Lista de todos os alunos registrados no sistema.")

    alunos = _listar_alunos()

    if not alunos:
        st.info("Nenhum aluno cadastrado ainda ou API indisponível.")
        return

    st.markdown(f"**{len(alunos)} aluno(s) encontrado(s)**")
    st.divider()

    # Cabeçalho
    cols = st.columns([2, 2.5, 1.5, 1.2, 1])
    for label, col in zip(["Nome", "E-mail", "Área", "Experiência", "Tasks"], cols):
        col.markdown(f"<small><b>{label}</b></small>", unsafe_allow_html=True)
    st.markdown('<hr style="margin:4px 0 8px 0;border-color:#1e3040;">', unsafe_allow_html=True)

    for a in alunos:
        cols = st.columns([2, 2.5, 1.5, 1.2, 1])
        cols[0].markdown(f"<span style='color:#e8f4ff;'>{a.get('nome','—')}</span>", unsafe_allow_html=True)
        cols[1].markdown(f"<span style='color:#8ab0c8;font-size:.85rem;'>{a.get('email','—')}</span>", unsafe_allow_html=True)
        cols[2].markdown(f"<span style='color:#c8d6e5;'>{a.get('area','—')}</span>", unsafe_allow_html=True)
        cols[3].markdown(f"<span style='color:#c8d6e5;'>{a.get('experiencia','—')}</span>", unsafe_allow_html=True)
        cols[4].markdown(f"<span style='color:#f0c040;font-weight:700;'>{a.get('total_sessoes', 0)}</span>", unsafe_allow_html=True)
