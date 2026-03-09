"""
telas/pg_login.py
Tela de login centralizada do AprovAI — tema escuro verde.
"""

import os
import base64
import streamlit as st
from database import verificar_login
from api_client import api_login


def render() -> bool:
    """
    Exibe a tela de login centralizada com tema escuro.
    Retorna False (autenticação ocorre via st.rerun após sucesso).
    """

    # Oculta sidebar e ajusta fundo e padding para a tela de login
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"]       { display: none !important; }
        [data-testid="stHeader"]        { display: none !important; }
        .block-container                { padding-top: 0 !important; max-width: 100% !important; }
        .stApp                          { background: linear-gradient(135deg, #071318 0%, #0d2b22 60%, #092318 100%) !important; }
        footer                          { display: none !important; }
        #MainMenu                       { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Espaçamento topo para centralizar verticalmente
    st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)

    # Colunas para centralizar o card
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        # Logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
        if os.path.exists(logo_path):
            img_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
            st.markdown(
                f'<div class="login-logo">'
                f'<img src="data:image/png;base64,{img_b64}" style="width:100px;margin-bottom:6px;" />'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="login-logo"><span>Aprov<em>AI</em></span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p class="login-subtitle">Gestao Inteligente de Concursos</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h4 style="color:#c8e8d8;font-size:1rem;margin-bottom:16px;">Acesse sua conta</h4>',
            unsafe_allow_html=True,
        )

        email = st.text_input(
            "E-mail",
            placeholder="seu@email.com",
            key="login_email",
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="••••••••",
            key="login_senha",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Entrar", use_container_width=True, type="primary"):
            if not email:
                st.error("Preencha o e-mail.")
            else:
                usuario = verificar_login(email, senha)
                if usuario:
                    st.session_state.usuario = usuario
                    st.session_state.autenticado = True
                    # Guarda credenciais para buscar JWT na próxima renderização
                    # (evita bloquear a transição da tela de login)
                    st.session_state._jwt_email = email
                    st.session_state._jwt_senha = senha
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<p style="text-align:center;color:#1e5c3a;font-size:0.72rem;margin-top:20px;">'
            'AprovAI &copy; 2025</p>',
            unsafe_allow_html=True,
        )

    return False
