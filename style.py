"""
style.py
Identidade visual da plataforma.
Chame aplicar_estilo() logo apos st.set_page_config() no app.py.

Paleta dark:
    #111e2b  — fundo principal (dark navy)
    #19293a  — cards / metricas
    #0d1b2a  — sidebar
    #00b4a6  — teal (destaque, ativo, hover)
    #d0e4f0  — texto geral claro
    #8ab0c8  — texto secundario
"""

import streamlit as st


def aplicar_estilo():
    st.markdown(
        """
        <style>

        /* ── Ocultar elementos nativos do Streamlit ──────────────────────── */
        [data-testid="stToolbar"]         { display: none !important; }
        [data-testid="stDecoration"]      { display: none !important; }
        [data-testid="stStatusWidget"]    { display: none !important; }
        #MainMenu                         { display: none !important; }
        footer                            { display: none !important; }
        header[data-testid="stHeader"]    { display: none !important; }

        /* ── Bloco principal ─────────────────────────────────────────────── */
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.5rem;
        }

        /* ── Fundo geral: dark navy ──────────────────────────────────────── */
        .stApp {
            background-color: #111e2b !important;
        }

        /* ── Texto geral ─────────────────────────────────────────────────── */
        .stApp, .stApp p, .stApp span, .stApp div,
        .stApp label, .stApp li {
            color: #d0e4f0;
        }

        h1 {
            color: #e8f4ff !important;
            font-weight: 700;
        }
        h2, h3, h4 {
            color: #c8dff0 !important;
        }

        /* ── Sidebar: fundo azul escuro ──────────────────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #0d1b2a !important;
            border-right: 1px solid #1a3a5c;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: #1a3a5c !important;
        }

        /* ── Botoes do menu lateral ──────────────────────────────────────── */
        [data-testid="stSidebar"] .stButton > button {
            background-color: transparent;
            color: #ffffff !important;
            border: 1px solid #1e4a6a;
            border-radius: 8px;
            text-align: left;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            width: 100%;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #00b4a6;
            color: #ffffff !important;
            border-color: #00b4a6;
        }

        [data-testid="stSidebar"] .stButton > button[kind="primaryFormSubmit"],
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background-color: #00b4a6 !important;
            border-color: #00b4a6 !important;
            color: #ffffff !important;
        }

        /* ── Cards de metricas ───────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background-color: #19293a !important;
            border-radius: 10px;
            padding: 18px 20px 14px 20px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
            border-top: 3px solid #00b4a6;
        }

        [data-testid="stMetricLabel"] p {
            color: #8ab0c8 !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: #e8f4ff !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
        }

        /* ── Inputs e selects ────────────────────────────────────────────── */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        textarea {
            background-color: #162535 !important;
            color: #d0e4f0 !important;
            border-color: #1e4a6a !important;
            border-radius: 8px !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #00b4a6 !important;
            box-shadow: 0 0 0 2px rgba(0,180,166,0.2) !important;
        }

        /* Dropdown das selects */
        [data-testid="stSelectbox"] svg,
        [data-testid="stSelectbox"] span {
            color: #d0e4f0 !important;
        }

        /* ── Tabelas (st.dataframe) ──────────────────────────────────────── */
        [data-testid="stDataFrame"] thead tr th {
            background-color: #0d1b2a !important;
            color: #ffffff !important;
            font-size: 0.76rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stDataFrame"] tbody tr td {
            background-color: #162535 !important;
            color: #d0e4f0 !important;
        }

        [data-testid="stDataFrame"] tbody tr:nth-child(even) td {
            background-color: #19293a !important;
        }

        [data-testid="stDataFrame"] tbody tr:hover td {
            background-color: #1e3a50 !important;
        }

        /* ── Divider ─────────────────────────────────────────────────────── */
        hr {
            border-color: #1e3a50 !important;
        }

        /* ── Scrollbar customizada ───────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #111e2b; }
        ::-webkit-scrollbar-thumb { background: #00b4a6; border-radius: 3px; }

        /* ── Alertas ─────────────────────────────────────────────────────── */
        [data-testid="stAlert"] {
            border-radius: 8px;
        }

        /* ── Expander ────────────────────────────────────────────────────── */
        [data-testid="stExpander"] {
            border: 1px solid #1e4a6a !important;
            border-radius: 8px !important;
            background-color: #162535 !important;
        }

        [data-testid="stExpander"] summary {
            color: #d0e4f0 !important;
        }

        /* ── Tabs ────────────────────────────────────────────────────────── */
        [data-testid="stTabs"] [role="tablist"] {
            border-bottom: 2px solid #1e4a6a;
        }

        [data-testid="stTabs"] button[role="tab"] {
            color: #8ab0c8 !important;
            font-weight: 500;
        }

        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #00b4a6 !important;
            border-bottom: 2px solid #00b4a6 !important;
            font-weight: 700;
        }

        /* ── Botoes principais ───────────────────────────────────────────── */
        .stButton > button[kind="primary"] {
            background-color: #00b4a6 !important;
            border-color: #00b4a6 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #009e91 !important;
        }

        .stButton > button[kind="secondary"] {
            background-color: #162535 !important;
            border-color: #1e4a6a !important;
            color: #d0e4f0 !important;
            border-radius: 8px !important;
        }

        .stButton > button[kind="secondary"]:hover {
            border-color: #00b4a6 !important;
            color: #00b4a6 !important;
        }

        /* ── Topbar: popover de usuario ──────────────────────────────────── */
        div[data-testid="stPopover"] > button,
        div[data-testid="stPopover"] > div > button {
            background-color: #19293a !important;
            color: #d0e4f0 !important;
            border: 1px solid #1e4a6a !important;
            border-radius: 24px !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            padding: 6px 14px !important;
            transition: all 0.2s;
        }

        div[data-testid="stPopover"] > button:hover {
            background-color: #00b4a6 !important;
            border-color: #00b4a6 !important;
        }

        .topbar-avatar {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00b4a6, #0d1b2a);
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 8px auto;
        }

        .topbar-nome {
            text-align: center;
            font-weight: 700;
            font-size: 0.95rem;
            color: #e8f4ff !important;
            margin: 0;
        }

        .topbar-email {
            text-align: center;
            font-size: 0.75rem;
            color: #8ab0c8 !important;
            margin: 2px 0 0 0;
        }

        /* ── Credito do autor na sidebar ─────────────────────────────────── */
        .sidebar-author {
            text-align: center;
            font-size: 0.70rem;
            color: #3a6080 !important;
            padding: 2px 0 0 0;
            letter-spacing: 0.02em;
        }

        /* ── Tela de login: fundo escuro ─────────────────────────────────── */
        .login-card {
            background: #0f2318;
            border-radius: 16px;
            padding: 44px 36px 36px 36px;
            width: 100%;
            box-shadow: 0 8px 40px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,180,100,0.15);
            border-top: 3px solid #00c48a;
            margin-top: 4vh;
        }

        .login-logo {
            text-align: center;
            margin-bottom: 6px;
        }

        .login-logo span {
            font-size: 2.2rem;
            font-weight: 800;
            color: #e0f0ea;
            letter-spacing: -1px;
        }

        .login-logo span em {
            color: #00c48a;
            font-style: normal;
        }

        .login-subtitle {
            text-align: center;
            color: #3d7a60;
            font-size: 0.80rem;
            margin-bottom: 28px;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .login-card h4, .login-card h3 {
            color: #c8e8d8 !important;
            font-size: 1rem !important;
            margin-bottom: 4px !important;
        }

        .login-card label, .login-card p {
            color: #7ab89a !important;
        }

        .login-card .stTextInput > div > div > input {
            background-color: #071e14 !important;
            border: 1.5px solid #1a4d35 !important;
            border-radius: 8px !important;
            color: #d0ead8 !important;
            font-size: 0.95rem !important;
            transition: border-color 0.2s;
        }

        .login-card .stTextInput > div > div > input::placeholder {
            color: #2e6648 !important;
        }

        .login-card .stTextInput > div > div > input:focus {
            border-color: #00c48a !important;
            box-shadow: 0 0 0 3px rgba(0,196,138,0.14) !important;
        }

        .login-card .stButton > button {
            background-color: #00a872 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            padding: 12px !important;
            width: 100%;
            transition: background-color 0.2s;
            margin-top: 8px;
            letter-spacing: 0.03em;
        }

        .login-card .stButton > button:hover {
            background-color: #00c48a !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
