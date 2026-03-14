"""
telas/pg_login_admin.py
Tela de login exclusiva para o administrador do sistema.
"""

import streamlit as st
from database import verificar_login

_CSS = """
<style>
[data-testid="stSidebar"]    { display:none!important }
[data-testid="stHeader"]     { display:none!important }
footer                       { display:none!important }
#MainMenu                    { display:none!important }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.stApp {
    background: #050d14 !important;
}

/* Card central */
.adm-card {
    background: linear-gradient(160deg, #0d1b2a 0%, #0f2035 100%);
    border: 1px solid #1a3a55;
    border-radius: 16px;
    padding: 48px 44px 40px 44px;
    box-shadow: 0 8px 40px rgba(0,0,0,.5);
}

/* Inputs */
.adm-wrap .stTextInput > div > div > input {
    background: #0a1628 !important;
    border: 1.5px solid #1e3a55 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: .95rem !important;
}
.adm-wrap .stTextInput > div > div > input:focus {
    border-color: #3a86ff !important;
    box-shadow: 0 0 0 3px rgba(58,134,255,.18) !important;
}
.adm-wrap .stTextInput label {
    color: #7a9ab8 !important;
    font-size: .82rem !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
}

/* Botão entrar */
.adm-wrap .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3a86ff, #1a66df) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: .04em !important;
}
/* Botão voltar */
.adm-wrap .stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #4a6a8a !important;
    border: 1px solid #1e3a55 !important;
    border-radius: 8px !important;
    font-size: .82rem !important;
}
</style>
"""


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    # Centraliza verticalmente com espaçamento
    st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        st.markdown("<div class='adm-wrap'>", unsafe_allow_html=True)

        # Ícone + título
        st.markdown(
            '<div style="text-align:center;margin-bottom:32px;">'
            '<div style="font-size:2.2rem;margin-bottom:10px;">⚙️</div>'
            '<div style="color:#e8f4ff;font-size:1.35rem;font-weight:800;letter-spacing:-.01em;">'
            'Painel Administrativo</div>'
            '<div style="color:#3a6080;font-size:.8rem;margin-top:4px;">Acesso restrito</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="adm-card">', unsafe_allow_html=True)

        usuario_input = st.text_input("Usuário", placeholder="admin", key="adm_usuario")
        senha_input   = st.text_input("Senha",   type="password", placeholder="••••••••", key="adm_senha")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Entrar no painel", use_container_width=True, type="primary", key="adm_btn_entrar"):
            if not usuario_input.strip():
                st.error("Informe o usuário.")
            else:
                u = verificar_login(usuario_input.strip(), senha_input)
                if u and u.get("role") == "administrador":
                    st.session_state.usuario     = u
                    st.session_state.autenticado = True
                    st.session_state.pagina      = "admin_hub"
                    # Token JWT para chamadas à API
                    try:
                        from api_client import api_login as _api_login
                        token = _api_login(u["email"], senha_input, nome=u.get("nome", ""))
                        if token:
                            st.session_state.api_token = token
                    except Exception:
                        pass
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        if st.button("← Voltar ao login de alunos", use_container_width=True, key="adm_btn_voltar"):
            st.session_state.pop("login_mode", None)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
