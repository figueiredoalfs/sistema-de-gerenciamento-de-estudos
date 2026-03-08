"""
app.py
Ponto de entrada da plataforma.

Como rodar:
    python -m streamlit run app.py
"""

import os
import base64
import streamlit as st
from database import inicializar_banco
from style import aplicar_estilo
from config_app import APP_NAME, APP_SLOGAN, APP_AUTHOR, LOGO_FILE

# ── Configuracao da pagina ────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilo()
inicializar_banco()

# ── Autenticacao ──────────────────────────────────────────────────────────────
if not st.session_state.get("autenticado"):
    from telas.pg_login import render as pg_login
    pg_login()
    st.stop()

# ── Importa as telas ─────────────────────────────────────────────────────────
from telas.pg_dashboard       import render as pg_dashboard
from telas.pg_lancar_bateria  import render as pg_lancar
from telas.pg_registrar_erros import render as pg_registrar_erros
from telas.pg_historico       import render as pg_historico
from telas.pg_erros_criticos  import render as pg_erros_criticos
from telas.pg_evolucao_mensal import render as pg_grafico
from telas.pg_cadastro        import render as pg_cadastro
from telas.pg_analise_erros   import render as pg_analise_erros
from telas.pg_perfil          import render as pg_perfil

# ── Inicializa o estado de navegacao ─────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

# ── Sidebar de navegacao ──────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), LOGO_FILE)
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
        f'<p class="sidebar-author">Desenvolvido por {APP_AUTHOR}</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    menu = [
        ("dashboard",      "Desempenho"),
        ("lancar",         "Lancar Bateria"),
        ("historico",      "Historico"),
        ("analise_erros",  "Analise de Erros"),
        ("erros_criticos", "Erros Criticos"),
        ("grafico",        "Evolucao Mensal"),
        ("cadastro",       "Cadastro"),
    ]

    for chave, label in menu:
        ativo = (st.session_state.pagina == chave)
        if st.button(
            label,
            key=f"nav_{chave}",
            use_container_width=True,
            type="primary" if ativo else "secondary",
        ):
            st.session_state.pop("id_bateria_erros",   None)
            st.session_state.pop("mats_bateria_erros", None)
            st.session_state.pop("erros_registrados",  None)
            st.session_state.pagina = chave
            st.rerun()

    st.divider()
    usuario_sb = st.session_state.get("usuario", {})
    st.markdown(
        f'<p style="color:#8ab0c8;font-size:0.78rem;text-align:center;padding:0 8px 4px 8px;">'
        f'{usuario_sb.get("nome","")}</p>',
        unsafe_allow_html=True,
    )
    if st.button("Sair", key="btn_logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ── Topbar superior direito (popover perfil + logoff) ────────────────────────
usuario = st.session_state.get("usuario", {})
nome_usuario = usuario.get("nome", "Usuario")
iniciais = "".join(p[0].upper() for p in nome_usuario.split()[:2])

_, col_user = st.columns([7, 1.5])
with col_user:
    with st.popover(f"{iniciais}  {nome_usuario}", use_container_width=True):
        st.markdown(
            f'<div class="topbar-avatar">{iniciais}</div>'
            f'<p class="topbar-nome">{nome_usuario}</p>'
            f'<p class="topbar-email">{usuario.get("email","")}</p>',
            unsafe_allow_html=True,
        )
        st.divider()
        if st.button("Meu Perfil", key="pop_perfil", use_container_width=True):
            st.session_state.pagina = "perfil"
            st.rerun()
        if st.button("Sair", key="pop_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ── Roteamento de paginas ─────────────────────────────────────────────────────
pagina = st.session_state.pagina

if pagina == "dashboard":
    pg_dashboard()
elif pagina == "lancar":
    pg_lancar()
elif pagina == "registrar_erros":
    pg_registrar_erros()
elif pagina == "historico":
    pg_historico()
elif pagina == "analise_erros":
    pg_analise_erros()
elif pagina == "erros_criticos":
    pg_erros_criticos()
elif pagina == "grafico":
    pg_grafico()
elif pagina == "cadastro":
    pg_cadastro()
elif pagina == "perfil":
    pg_perfil()
