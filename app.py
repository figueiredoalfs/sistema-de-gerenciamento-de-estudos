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
from telas.components import timer_bar

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
    st.markdown(
        "<style>.stApp{background:none!important}</style>",
        unsafe_allow_html=True,
    )
    from telas.pg_login import render as pg_login
    pg_login()
    st.stop()

# ── Timer de estudo no topo (client-side JS) ──────────────────────────────────
st.markdown(timer_bar(), unsafe_allow_html=True)

# ── Importa as telas ─────────────────────────────────────────────────────────
from telas.pg_dashboard       import render as pg_dashboard
from telas.pg_lancar_bateria  import render as pg_lancar
from telas.pg_historico       import render as pg_historico
from telas.pg_erros_criticos  import render as pg_erros_criticos
from telas.pg_evolucao_mensal import render as pg_grafico
from telas.pg_analise_erros   import render as pg_analise_erros
from telas.pg_perfil          import render as pg_perfil
from telas.pg_onboarding      import render as pg_onboarding
from telas.pg_plano           import render as pg_plano

# ── Onboarding: redireciona novos usuarios ────────────────────────────────────
if not st.session_state.get("onboarding_concluido"):
    from database import get_perfil as _get_perfil
    _perfil_db = _get_perfil(st.session_state.usuario["id"])
    if _perfil_db.get("plano") == "ativo":
        st.session_state.onboarding_concluido = True
    else:
        if "ob_tela" not in st.session_state:
            st.session_state.ob_tela = 1
        st.session_state.pagina = "onboarding"

# ── Inicializa o estado de navegacao ─────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "plano"

# ── Sidebar de navegacao ──────────────────────────────────────────────────────
with st.sidebar:
    # Logo ou nome do app
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

    # Menu com ícones
    MENU_ITEMS = [
        ("plano",          "🏠", "Agenda do Dia"),
        ("dashboard",      "📊", "Desempenho"),
        ("lancar",         "✏️",  "Lançar Bateria"),
        ("historico",      "🕐", "Histórico"),
        ("analise_erros",  "🔍", "Análise de Erros"),
        ("erros_criticos", "⚠️", "Erros Críticos"),
        ("grafico",        "📈", "Evolução Mensal"),
        ("perfil",         "👤", "Meu Perfil"),
    ]

    for chave, icone, label in MENU_ITEMS:
        ativo = (st.session_state.pagina == chave)
        texto = f"{icone}  {label}"
        if st.button(
            texto,
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

    # Nome do usuário + sair
    usuario_sb = st.session_state.get("usuario", {})
    st.markdown(
        f'<p style="color:#8ab0c8;font-size:0.78rem;text-align:center;padding:0 8px 4px 8px;">'
        f'{usuario_sb.get("nome","")}</p>',
        unsafe_allow_html=True,
    )
    if st.button("Sair", key="btn_logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # ── Painel DEV ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#f39c12;font-size:0.68rem;font-weight:700;text-align:center;'
        'letter-spacing:0.1em;">⚡ DEV</p>',
        unsafe_allow_html=True,
    )

    uid_atual  = st.session_state.get("usuario", {}).get("id", "?")
    nome_atual = st.session_state.get("usuario", {}).get("nome", "?")
    st.markdown(
        f'<p style="color:#3a6080;font-size:0.68rem;text-align:center;margin:0 0 6px 0;">'
        f'Usuário: <b style="color:#5a8aaa;">{nome_atual}</b> (id={uid_atual})</p>',
        unsafe_allow_html=True,
    )

    if st.button("Carregar Dados de Teste", key="btn_carregar_teste", use_container_width=True):
        from database import gerar_dados_teste
        from telas.pg_dashboard import _fetch_lancamentos
        result = gerar_dados_teste(st.session_state.usuario["id"])
        _fetch_lancamentos.clear()
        st.session_state.onboarding_concluido = True
        email_atual = st.session_state.get("usuario", {}).get("email", "")
        if email_atual and st.session_state.get("api_token"):
            try:
                from app.scripts.seed_sessoes_teste import seed_sessoes
                seed_sessoes(email_atual)
            except Exception:
                pass
        st.session_state.pagina = "plano"
        st.toast(f"Dados de teste carregados! {result['baterias']} baterias geradas.")
        st.rerun()

    if st.button("Resetar Dados", key="btn_reset_usuario", use_container_width=True):
        from database import resetar_usuario
        resetar_usuario(st.session_state.usuario["id"])
        for k in list(st.session_state.keys()):
            if k.startswith("ob_") or k == "onboarding_concluido":
                del st.session_state[k]
        st.session_state.ob_tela = 1
        st.session_state.pagina  = "onboarding"
        st.rerun()

    if st.button("Trocar Usuário", key="btn_trocar_usuario", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ── Roteamento de paginas ─────────────────────────────────────────────────────
pagina = st.session_state.pagina

if pagina == "dashboard":
    pg_dashboard()
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
elif pagina == "perfil":
    pg_perfil()
elif pagina == "onboarding":
    pg_onboarding()
elif pagina == "plano":
    pg_plano()
