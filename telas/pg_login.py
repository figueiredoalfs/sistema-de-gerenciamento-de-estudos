"""
telas/pg_login.py
Layout split com features animadas no painel esquerdo.
Nome "AprovAI" é provisório.
"""

import os
import base64
import streamlit as st
from database import verificar_login, criar_usuario
from config_app import EMAIL_CONFIRMACAO_ATIVO, APP_AUTHOR


def render() -> bool:

    # ── Logo ──────────────────────────────────────────────────────────────────
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
    if os.path.exists(logo_path):
        img_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
        logo_html = f'<img src="data:image/png;base64,{img_b64}" style="width:80px;display:block;margin-bottom:28px;" />'
    else:
        logo_html = '<div style="font-size:1.8rem;font-weight:900;color:#00b4a6;margin-bottom:28px;">AprovAI</div>'

    # ── CSS ───────────────────────────────────────────────────────────────────
    st.markdown("""<style>
[data-testid="stSidebar"]{display:none!important}
[data-testid="stHeader"]{display:none!important}
footer{display:none!important}
#MainMenu{display:none!important}
.block-container{padding:0!important;max-width:100%!important}
.stApp{background:linear-gradient(150deg,#061020 0%,#0d1b2a 60%,#0a2235 100%)!important}

/* Colunas sem gap */
[data-testid="stHorizontalBlock"]{gap:0!important;align-items:stretch!important}

/* Padding interno da coluna esquerda */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:first-child>div{
    padding:52px 40px 52px 60px!important
}

/* Coluna direita: fundo escuro-azulado + centralização vertical */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:last-child{
    background:linear-gradient(160deg,#0f2035 0%,#102840 100%)!important;
    border-left:1px solid #1a3a55!important
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:last-child>div{
    padding:0 60px!important;
    display:flex!important;
    flex-direction:column!important;
    justify-content:center!important;
    min-height:100vh!important
}

/* Abas no tema escuro */
[data-testid="stColumn"]:last-child [data-testid="stTabs"] [data-testid="stTab"] p{
    color:#8ab0c8!important;font-weight:600!important
}
[data-testid="stColumn"]:last-child [data-testid="stTabs"] [aria-selected="true"] p{
    color:#00b4a6!important
}

/* Inputs no tema escuro */
[data-testid="stColumn"]:last-child .stTextInput>div>div>input{
    background:#1e3a55!important;border:1.5px solid #2e5070!important;
    border-radius:8px!important;color:#ffffff!important;font-size:.95rem!important
}
[data-testid="stColumn"]:last-child .stTextInput>div>div>input:focus{
    border-color:#00b4a6!important;box-shadow:0 0 0 3px rgba(0,180,166,.2)!important;
    background:#1e3a55!important
}
[data-testid="stColumn"]:last-child .stTextInput>div>div>input::placeholder{
    color:#6a8aaa!important;opacity:1!important
}
[data-testid="stColumn"]:last-child .stTextInput label{
    color:#a0c0d8!important;font-size:.83rem!important;font-weight:600!important
}
/* Garantir cor do texto digitado (webkit) */
[data-testid="stColumn"]:last-child .stTextInput>div>div>input:-webkit-autofill{
    -webkit-text-fill-color:#ffffff!important;
    -webkit-box-shadow:0 0 0 100px #1e3a55 inset!important
}

/* Botões */
[data-testid="stColumn"]:last-child .stButton>button[kind="primary"]{
    background:linear-gradient(135deg,#00b4a6,#009688)!important;color:#fff!important;
    border:none!important;border-radius:8px!important;font-weight:700!important;letter-spacing:.04em!important
}
[data-testid="stColumn"]:last-child .stButton>button[kind="secondary"]{
    background:transparent!important;color:#00b4a6!important;
    border:1.5px solid #00b4a6!important;border-radius:8px!important;font-weight:600!important
}

/* Animação das features */
@keyframes feat-show {
    0%   { opacity:0; transform:translateY(12px); }
    8%   { opacity:1; transform:translateY(0); }
    25%  { opacity:1; transform:translateY(0); }
    33%  { opacity:0; transform:translateY(-8px); }
    100% { opacity:0; transform:translateY(-8px); }
}
.feat-wrap{position:relative;height:72px;margin-bottom:40px;}
.feat-item{
    position:absolute;top:0;left:0;
    display:flex;align-items:flex-start;gap:12px;
    opacity:0;
    animation:feat-show 12s infinite;
}
.feat-item:nth-child(1){animation-delay:0s}
.feat-item:nth-child(2){animation-delay:3s}
.feat-item:nth-child(3){animation-delay:6s}
.feat-item:nth-child(4){animation-delay:9s}
.feat-dot{
    width:36px;height:36px;border-radius:50%;
    background:rgba(0,180,166,.18);border:1px solid rgba(0,180,166,.35);
    display:flex;align-items:center;justify-content:center;
    font-size:.95rem;flex-shrink:0;margin-top:2px;
}
.feat-text{color:#c8d6e5;font-size:1.08rem;line-height:1.4;}
</style>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 0.9], gap="small")

    # ════════════════════════════════════════════════════════════════════════
    # PAINEL ESQUERDO
    # ════════════════════════════════════════════════════════════════════════
    with col_left:
        st.markdown(logo_html, unsafe_allow_html=True)

        st.markdown(
            '<div style="display:inline-block;background:rgba(0,180,166,.12);border:1px solid rgba(0,180,166,.35);'
            'color:#00b4a6;font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;'
            'padding:4px 14px;border-radius:20px;margin-bottom:24px;">Plataforma de Concursos com IA</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="color:#fff;font-size:2rem;font-weight:900;line-height:1.2;letter-spacing:-.02em;margin-bottom:14px;">'
            'Estude com <span style="color:#00b4a6;">inteligência</span>.<br>Passe mais rápido.</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p style="color:#7a9ab8;font-size:.95rem;line-height:1.65;max-width:400px;margin-bottom:32px;">'
            'Transforme seu edital em um plano de estudos adaptativo e otimize cada hora de estudo com IA.</p>',
            unsafe_allow_html=True,
        )

        # Features animadas — um único st.markdown para o CSS funcionar
        st.markdown("""<div class="feat-wrap">
<div class="feat-item"><div class="feat-dot">&#128203;</div><span class="feat-text">Plano de estudos gerado automaticamente pelo seu edital</span></div>
<div class="feat-item"><div class="feat-dot">&#129302;</div><span class="feat-text">IA que detecta seus erros e prioriza as revisões certas</span></div>
<div class="feat-item"><div class="feat-dot">&#128200;</div><span class="feat-text">Desempenho por matéria com análise de tendência</span></div>
<div class="feat-item"><div class="feat-dot">&#127919;</div><span class="feat-text">Cronograma adaptativo até a data da sua prova</span></div>
</div>""", unsafe_allow_html=True)

        st.markdown(f'<p style="color:#2a4a6a;font-size:.7rem;margin-top:8px;">AprovAI &copy; 2025 &nbsp;&middot;&nbsp; by {APP_AUTHOR}</p>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # PAINEL DIREITO
    # ════════════════════════════════════════════════════════════════════════
    with col_right:
        tab_login, tab_cadastro = st.tabs(["  Entrar  ", "  Criar conta  "])

        with tab_login:
            st.markdown(
                '<p style="color:#e8f0f8;font-size:1.4rem;font-weight:800;margin-bottom:2px;">Bem-vindo de volta</p>'
                '<p style="color:#5a8aaa;font-size:.87rem;margin-bottom:18px;">Acesse sua conta para continuar</p>',
                unsafe_allow_html=True,
            )
            email_l = st.text_input("E-mail", placeholder="seu@email.com", key="login_email")
            senha_l = st.text_input("Senha", type="password", placeholder="••••••••", key="login_senha")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if st.button("Entrar", use_container_width=True, type="primary", key="btn_entrar"):
                if not email_l.strip():
                    st.error("Preencha o e-mail.")
                else:
                    usuario = verificar_login(email_l.strip(), senha_l)
                    if usuario:
                        # Bloqueia login se confirmação de e-mail estiver ativa e pendente
                        if EMAIL_CONFIRMACAO_ATIVO and not usuario.get("email_confirmado", True):
                            st.warning("Confirme seu e-mail antes de entrar. Verifique sua caixa de entrada.")
                        else:
                            st.session_state.usuario     = usuario
                            st.session_state.autenticado = True
                            st.session_state._jwt_email  = email_l.strip()
                            st.session_state._jwt_senha  = senha_l
                            st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")

        with tab_cadastro:
            st.markdown(
                '<p style="color:#e8f0f8;font-size:1.4rem;font-weight:800;margin-bottom:2px;">Crie sua conta</p>'
                '<p style="color:#5a8aaa;font-size:.87rem;margin-bottom:18px;">Gratuito, sem cartão de crédito</p>',
                unsafe_allow_html=True,
            )
            nome_c   = st.text_input("Nome completo", placeholder="Seu nome", key="cad_nome")
            email_c  = st.text_input("E-mail", placeholder="seu@email.com", key="cad_email")
            senha_c  = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres", key="cad_senha")
            senha_c2 = st.text_input("Confirmar senha", type="password", placeholder="••••••••", key="cad_senha2")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if st.button("Criar conta", use_container_width=True, type="primary", key="btn_cadastrar"):
                if not nome_c.strip():
                    st.error("Informe seu nome.")
                elif not email_c.strip():
                    st.error("Informe seu e-mail.")
                elif len(senha_c) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif senha_c != senha_c2:
                    st.error("As senhas não coincidem.")
                else:
                    ok = criar_usuario(nome_c.strip(), email_c.strip(), senha_c)
                    if ok:
                        if EMAIL_CONFIRMACAO_ATIVO:
                            # Confirmação de e-mail ativa (Railway): stub — implementar envio real
                            # TODO: gerar token, salvar no DB e enviar e-mail com link de confirmação
                            st.success("Conta criada! Verifique seu e-mail para confirmar o cadastro.")
                        else:
                            # Dev local: login automático sem confirmação
                            usuario = verificar_login(email_c.strip(), senha_c)
                            if usuario:
                                st.session_state.usuario     = usuario
                                st.session_state.autenticado = True
                                st.session_state._jwt_email  = email_c.strip()
                                st.session_state._jwt_senha  = senha_c
                                st.rerun()
                    else:
                        st.error("Este e-mail já está cadastrado.")

    return False
