"""
app.py
Ponto de entrada do SISFIG — Gestao de Desempenho em Concursos.

Como rodar:
    streamlit run app.py
"""

import streamlit as st
from database import inicializar_banco

# ── Configuracao da pagina ────────────────────────────────────────────────────
st.set_page_config(
    page_title="SISFIG",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# ── Inicializa o estado de navegacao ─────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

# ── Sidebar de navegacao ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# SISFIG")
    st.caption("Gestao de Concursos")
    st.divider()

    # Itens do menu: (chave_interna, texto_exibido)
    menu = [
        ("dashboard",      "Dashboard"),
        ("lancar",         "Lancar Bateria"),
        ("historico",      "Historico"),
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
elif pagina == "erros_criticos":
    pg_erros_criticos()
elif pagina == "grafico":
    pg_grafico()
elif pagina == "cadastro":
    pg_cadastro()
