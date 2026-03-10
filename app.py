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
    # Reseta qualquer CSS residual da sessão anterior antes de mostrar o login
    st.markdown(
        "<style>.stApp{background:none!important}</style>",
        unsafe_allow_html=True,
    )
    from telas.pg_login import render as pg_login
    pg_login()
    st.stop()

# ── Busca JWT em background (não bloqueia o render da tela) ──────────────────
# Resultado guardado em dict de módulo; consumido no próximo render.
import threading as _threading
_jwt_results: dict = {}  # user_id -> token

_uid_atual = st.session_state.get("usuario", {}).get("id", "")

# Inicia thread se há credenciais pendentes
if "api_token" not in st.session_state and "_jwt_email" in st.session_state:
    _email_bg = st.session_state.pop("_jwt_email")
    _senha_bg = st.session_state.pop("_jwt_senha")
    _nome_bg  = st.session_state.usuario.get("nome", "")

    def _fetch_jwt_bg(uid, email, senha, nome):
        from api_client import api_login as _al
        token = _al(email, senha, nome=nome)
        if token:
            _jwt_results[uid] = token

    _threading.Thread(
        target=_fetch_jwt_bg,
        args=(_uid_atual, _email_bg, _senha_bg, _nome_bg),
        daemon=True,
    ).start()

# Consome resultado da thread (disponível a partir da próxima interação)
if "api_token" not in st.session_state and _uid_atual in _jwt_results:
    st.session_state.api_token = _jwt_results.pop(_uid_atual)

# ── Importa as telas ─────────────────────────────────────────────────────────
from telas.pg_dashboard       import render as pg_dashboard
from telas.pg_lancar_bateria  import render as pg_lancar
from telas.pg_historico       import render as pg_historico
from telas.pg_erros_criticos  import render as pg_erros_criticos
from telas.pg_evolucao_mensal import render as pg_grafico
from telas.pg_cadastro        import render as pg_cadastro
from telas.pg_analise_erros   import render as pg_analise_erros
from telas.pg_perfil          import render as pg_perfil
from telas.pg_onboarding     import render as pg_onboarding
from telas.pg_plano          import render as pg_plano

# ── Onboarding: redireciona novos usuarios ────────────────────────────────────
if not st.session_state.get("onboarding_concluido"):
    from database import get_perfil as _get_perfil
    _perfil_db = _get_perfil(st.session_state.usuario["id"])
    if _perfil_db.get("plano") == "ativo":
        # Ja concluiu o onboarding anteriormente
        st.session_state.onboarding_concluido = True
    else:
        # Novo usuario — inicia onboarding
        if "ob_tela" not in st.session_state:
            st.session_state.ob_tela = 1
        st.session_state.pagina = "onboarding"

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
        ("plano",         "Meu Plano"),
        ("dashboard",     "Desempenho"),
        ("lancar",        "Lançar Bateria"),
        ("historico",     "Histórico"),
        ("analise_erros", "Análise de Erros"),
        ("grafico",       "Evolução Mensal"),
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

    # ── Painel DEV ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#f39c12;font-size:0.68rem;font-weight:700;text-align:center;'
        'letter-spacing:0.1em;">⚡ DEV</p>',
        unsafe_allow_html=True,
    )

    uid_atual = st.session_state.get("usuario", {}).get("id", "?")
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
        st.session_state.pagina = "dashboard"
        st.toast(
            f"✅ {result['baterias']} baterias · {result['lancamentos']} lançamentos · {result['erros']} erros gerados",
            icon="🧪",
        )
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
elif pagina == "onboarding":
    pg_onboarding()
elif pagina == "plano":
    pg_plano()
