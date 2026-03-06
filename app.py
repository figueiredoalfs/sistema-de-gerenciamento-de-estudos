"""
app.py
Ponto de entrada do AprovAI — Gestao de Desempenho em Concursos.

Como rodar:
    streamlit run app.py
"""

import os
import streamlit as st
from database import inicializar_banco
from style import aplicar_estilo

# ── Configuracao da pagina ────────────────────────────────────────────────────
st.set_page_config(
    page_title="AprovAI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Aplica a identidade visual (CSS customizado)
aplicar_estilo()

# Inicializa o banco SQLite na primeira execucao (cria tabelas se nao existirem)
inicializar_banco()

# ── Importa as telas ─────────────────────────────────────────────────────────
from telas.pg_dashboard       import render as pg_dashboard
from telas.pg_lancar_bateria  import render as pg_lancar
from telas.pg_registrar_erros import render as pg_registrar_erros
from telas.pg_historico       import render as pg_historico
from telas.pg_erros_criticos  import render as pg_erros_criticos
from telas.pg_evolucao_mensal import render as pg_grafico
from telas.pg_cadastro        import render as pg_cadastro
from telas.pg_analise_erros   import render as pg_analise_erros

# ── Inicializa o estado de navegacao ─────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

# ── Sidebar de navegacao ──────────────────────────────────────────────────────
with st.sidebar:
    # Logo (exibe se o arquivo existir)
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.markdown(
            f'<div style="display:flex;justify-content:center;padding:20px 0 4px 0;">'
            f'<img src="data:image/png;base64,{__import__("base64").b64encode(open(logo_path,"rb").read()).decode()}"'
            f' style="width:140px;object-fit:contain;" /></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align:center;padding:18px 14px 6px 14px;">'
            '<span style="font-size:1.6rem;font-weight:bold;color:#00b4a6;">AprovAI</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p style="color:#8ab0c8;font-size:0.78rem;text-align:center;padding:0 14px 8px 14px;">'
        "Gestao Inteligente de Concursos</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Itens do menu: (chave_interna, texto_exibido)
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
            # Ao navegar pelo menu limpa o estado de fluxo registrar_erros
            st.session_state.pop("id_bateria_erros",   None)
            st.session_state.pop("mats_bateria_erros", None)
            st.session_state.pop("erros_registrados",  None)
            st.session_state.pagina = chave
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
