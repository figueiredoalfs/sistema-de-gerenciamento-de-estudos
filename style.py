"""
style.py
Identidade visual do AprovAI.
Chame aplicar_estilo() logo apos st.set_page_config() no app.py.

Paleta:
    #0d1b2a  — azul escuro (sidebar, titulos)
    #00b4a6  — teal (destaque, ativo, hover)
    #f0f4f8  — cinza claro (fundo principal)
    #ffffff  — branco (cards, superficies)
    #1a1a2a  — texto escuro geral
"""

import streamlit as st


def aplicar_estilo():
    st.markdown(
        """
        <style>

        /* ── Bloco principal: remove padding excessivo do topo ───────────── */
        .block-container {
            padding-top: 1.5rem;
        }

        /* ── Fundo geral da pagina ───────────────────────────────────────── */
        .stApp {
            background-color: #f0f4f8;
        }

        /* ── Sidebar: fundo azul escuro ──────────────────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #0d1b2a;
            border-right: 1px solid #1a3a5c;
        }

        /* Garante que todo texto da sidebar seja branco */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }

        /* Divider dentro da sidebar */
        [data-testid="stSidebar"] hr {
            border-color: #1a3a5c !important;
        }

        /* ── Botoes do menu lateral ──────────────────────────────────────── */
        [data-testid="stSidebar"] .stButton > button {
            background-color: transparent;
            color: #ffffff !important;
            border: 1px solid #00b4a6;
            border-radius: 8px;
            text-align: left;
            font-size: 0.9rem;
            transition: background-color 0.2s ease, color 0.2s ease;
            width: 100%;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #00b4a6;
            color: #ffffff !important;
            border-color: #00b4a6;
        }

        /* Botao ativo (type="primary") */
        [data-testid="stSidebar"] .stButton > button[kind="primaryFormSubmit"],
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background-color: #00b4a6 !important;
            border-color: #00b4a6 !important;
            color: #ffffff !important;
        }

        /* ── Titulos das paginas ─────────────────────────────────────────── */
        h1 {
            color: #0d1b2a !important;
            font-weight: 700;
        }
        h2, h3 {
            color: #0d1b2a !important;
        }

        /* ── Cards de metricas (st.metric) ──────────────────────────────── */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 18px 20px 14px 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
            border-top: 3px solid #00b4a6;
        }

        /* Rotulo do metric */
        [data-testid="stMetricLabel"] p {
            color: #0d1b2a !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        /* Valor principal do metric */
        [data-testid="stMetricValue"] {
            color: #0d1b2a !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
        }

        /* ── Tabelas (st.dataframe) ──────────────────────────────────────── */
        [data-testid="stDataFrame"] thead tr th {
            background-color: #0d1b2a !important;
            color: #ffffff !important;
            font-size: 0.76rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stDataFrame"] tbody tr:nth-child(even) td {
            background-color: #f8fafc !important;
        }

        [data-testid="stDataFrame"] tbody tr:hover td {
            background-color: #e6f7f6 !important;
        }

        /* ── Scrollbar customizada ───────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #f0f4f8; }
        ::-webkit-scrollbar-thumb { background: #00b4a6; border-radius: 3px; }

        /* ── Alertas e banners harmonizados ─────────────────────────────── */
        [data-testid="stAlert"] {
            border-radius: 8px;
        }

        /* ── Expander com borda teal ─────────────────────────────────────── */
        [data-testid="stExpander"] {
            border: 1px solid #00b4a664 !important;
            border-radius: 8px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
