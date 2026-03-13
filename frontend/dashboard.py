"""
frontend/dashboard.py
Ponto de entrada do frontend Streamlit.

Como rodar:
    python -m streamlit run frontend/dashboard.py
"""

import os
import sys
import base64
import streamlit as st

# ── Caminhos ──────────────────────────────────────────────────────────────────
_FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR     = os.path.dirname(_FRONTEND_DIR)

# Adiciona frontend/ ao path (para importar api_client e telas.*)
if _FRONTEND_DIR not in sys.path:
    sys.path.insert(0, _FRONTEND_DIR)

# Adiciona raiz ao path (para importar config_app, config_fontes, config_materias)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from config_app import APP_NAME, APP_SLOGAN, APP_AUTHOR, LOGO_FILE

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Autenticação ──────────────────────────────────────────────────────────────
if not st.session_state.get("autenticado"):
    st.markdown(
        "<style>.stApp{background:none!important}</style>",
        unsafe_allow_html=True,
    )
    from telas.pg_login import render as _pg_login
    _pg_login()
    st.stop()

# ── Importa as telas ──────────────────────────────────────────────────────────
from telas.pg_desempenho      import render as pg_desempenho
from telas.pg_plano           import render as pg_plano
from telas.pg_lancar_bateria  import render as pg_lancar
from telas.pg_historico       import render as pg_historico
from telas.pg_erros_criticos  import render as pg_erros_criticos
from telas.pg_evolucao_mensal import render as pg_grafico
from telas.pg_analise_erros   import render as pg_analise_erros
from telas.pg_onboarding      import render as pg_onboarding

# ── Onboarding: verifica se o plano já foi configurado ───────────────────────
if not st.session_state.get("onboarding_concluido") and not st.session_state.get("_ob_check_done"):
    from api_client import get_agenda as _get_agenda
    sessoes = _get_agenda(top=1)
    st.session_state._ob_check_done = True
    if sessoes:
        st.session_state.onboarding_concluido = True
    else:
        if "ob_tela" not in st.session_state:
            st.session_state.ob_tela = 1
        st.session_state.pagina = "onboarding"

# ── Estado de navegação ───────────────────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "plano"

# ── Sidebar de navegação ──────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(_ROOT_DIR, LOGO_FILE)
    if os.path.exists(logo_path):
        img_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
        st.markdown(
            f'<div style="display:flex;justify-content:center;padding:20px 0 4px 0;">'
            f'<img src="data:image/png;base64,{img_b64}" style="width:140px;object-fit:contain;" />'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="text-align:center;padding:18px 14px 6px 14px;">'
            f'<span style="font-size:1.6rem;font-weight:bold;color:#00b4a6;">{APP_NAME}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<p style="color:#8ab0c8;font-size:0.78rem;text-align:center;'
        f'padding:0 14px 2px 14px;">{APP_SLOGAN}</p>'
        f'<p style="color:#3a6080;font-size:0.68rem;text-align:center;">'
        f'Desenvolvido por {APP_AUTHOR}</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    menu = [
        ("plano",         "Meu Plano"),
        ("dashboard",     "Desempenho"),
        ("lancar",        "Lançar Bateria"),
        ("historico",     "Histórico"),
        ("analise_erros", "Análise de Erros"),
        ("grafico",       "Evolução Mensal"),
    ]

    for chave, label in menu:
        ativo = st.session_state.pagina == chave
        if st.button(
            label,
            key=f"nav_{chave}",
            use_container_width=True,
            type="primary" if ativo else "secondary",
        ):
            # Limpa estado temporário de outras telas
            for k in ("id_bateria_erros", "mats_bateria_erros", "erros_registrados"):
                st.session_state.pop(k, None)
            st.session_state.pagina = chave
            st.rerun()

    st.divider()
    usuario_sb = st.session_state.get("usuario", {})
    st.markdown(
        f'<p style="color:#8ab0c8;font-size:0.78rem;text-align:center;padding:0 8px 4px 8px;">'
        f'{usuario_sb.get("nome", "")}</p>',
        unsafe_allow_html=True,
    )
    if st.button("Sair", key="btn_logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ── Topbar com perfil ─────────────────────────────────────────────────────────
usuario      = st.session_state.get("usuario", {})
nome_usuario = usuario.get("nome", "Usuário")
iniciais     = "".join(p[0].upper() for p in nome_usuario.split()[:2])

_, col_user = st.columns([7, 1.5])
with col_user:
    with st.popover(f"{iniciais}  {nome_usuario}", use_container_width=True):
        st.markdown(
            f'<p style="font-weight:800;font-size:1.1rem;color:#e8f0f8;">{nome_usuario}</p>'
            f'<p style="color:#8ab0c8;font-size:0.85rem;">{usuario.get("email", "")}</p>',
            unsafe_allow_html=True,
        )
        st.divider()
        if st.button("Sair", key="pop_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ── Roteamento de páginas ─────────────────────────────────────────────────────
pagina = st.session_state.pagina

if pagina == "dashboard":
    pg_desempenho()
elif pagina == "lancar":
    pg_lancar()
elif pagina == "historico":
    pg_historico()
elif pagina == "analise_erros":
    pg_analise_erros()
elif pagina == "erros_criticos":
    pg_erros_criticos()
elif pagina == "grafico":
    pg_grafico()
elif pagina == "onboarding":
    pg_onboarding()
elif pagina == "plano":
    pg_plano()
