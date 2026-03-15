"""
telas/pg_admin_hub.py — Dashboard principal do administrador.
"""

import requests
import streamlit as st

_API_BASE = "http://localhost:8000"


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _stat(label: str, valor, cor: str, icone: str):
    st.markdown(
        f'<div style="background:#0f1e2e;border:1px solid #1a3040;border-radius:12px;'
        f'padding:20px 24px;text-align:center;">'
        f'<div style="font-size:1.6rem;margin-bottom:6px;">{icone}</div>'
        f'<div style="font-size:1.7rem;font-weight:800;color:{cor};">{valor}</div>'
        f'<div style="color:#5a7a96;font-size:.8rem;margin-top:4px;">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _card_ferramenta(icone: str, titulo: str, desc: str, pagina: str, cor: str = "#3a86ff"):
    if st.button(
        f"{icone}  {titulo}",
        key=f"hub_{pagina}",
        use_container_width=True,
        help=desc,
    ):
        st.session_state.pagina = pagina
        st.rerun()
    st.markdown(
        f'<p style="color:#4a6a8a;font-size:.75rem;margin:-8px 0 12px 0;">{desc}</p>',
        unsafe_allow_html=True,
    )


def _fetch_stats() -> dict:
    try:
        r = requests.get(f"{_API_BASE}/admin/stats", headers=_headers(), timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def render():
    if st.session_state.get("usuario", {}).get("role") != "administrador":
        st.error("Acesso negado. Esta área é restrita a administradores.")
        st.stop()

    st.markdown(
        '<h2 style="margin-bottom:4px;">⚙️ Painel Administrativo</h2>'
        '<p style="color:#4a6a8a;font-size:.87rem;margin-bottom:28px;">'
        'Gerencie o sistema, configure ciclos e acompanhe métricas.</p>',
        unsafe_allow_html=True,
    )

    # ── Estatísticas rápidas ──────────────────────────────────────────────────
    stats = _fetch_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _stat("Alunos cadastrados", stats.get("total_alunos", "—"), "#3a86ff", "👥")
    with c2:
        _stat("Sessões geradas",    stats.get("total_sessoes", "—"), "#06d6a0", "📋")
    with c3:
        _stat("Matérias no ciclo",  stats.get("total_ciclos", "—"),  "#f77f00", "📚")
    with c4:
        _stat("Tópicos cadastrados",stats.get("total_topicos", "—"), "#9b5de5", "🗂️")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Ferramentas", unsafe_allow_html=False)
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        _card_ferramenta(
            "🔄", "Ciclos de Matérias",
            "Configure a ordem das matérias por área de concurso.",
            "admin_ciclos",
        )
        _card_ferramenta(
            "📂", "Tópicos",
            "Visualize e gerencie a hierarquia de tópicos do sistema.",
            "admin_topicos",
        )

    with col2:
        _card_ferramenta(
            "👥", "Usuários",
            "Consulte os alunos cadastrados e seus perfis.",
            "admin_usuarios",
            cor="#06d6a0",
        )
        _card_ferramenta(
            "📥", "Importar Questões",
            "Importe questões em lote via arquivo JSON ou CSV.",
            "admin_importar_questoes",
            cor="#f77f00",
        )
