"""
pg_historico.py
Historico paginado de baterias com filtro de periodo e coluna de status.
"""

import streamlit as st
import pandas as pd
from database import ler_lancamentos, ler_erros

PAGE_SIZE = 20


def render():
    st.html("""
        <div style="
            background: linear-gradient(135deg, #061020 0%, #0d1b2a 100%);
            border-radius: 10px;
            padding: 18px 24px;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #00b4a6;
            box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        ">
            <span style="font-size:1.4rem;">&#128203;</span>
            <span style="
                color:#ffffff;
                font-weight:800;
                font-size:1.3rem;
                letter-spacing:0.12em;
                margin-left:10px;
                text-transform:uppercase;
            ">HISTORICO DE BATERIAS</span>
        </div>
    """)

    df_l_all = ler_lancamentos(st.session_state.usuario["id"])
    df_e     = ler_erros(st.session_state.usuario["id"])

    # ── Filtro de periodo ──────────────────────────────────────────────────────
    meses_map = {
        "Todos": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
        "Mai": 5,      "Jun": 6, "Jul": 7, "Ago": 8,
        "Set": 9,      "Out": 10,"Nov": 11,"Dez": 12,
    }
    col_f1, col_f2, _ = st.columns([1, 1, 4])
    mes_sel = col_f1.selectbox("Mes", list(meses_map.keys()), key="hist_mes")

    anos_disp = ["Todos"]
    if not df_l_all.empty:
        dts = pd.to_datetime(df_l_all["Data"], dayfirst=True, errors="coerce").dropna()
        anos_disp += sorted(dts.dt.year.unique().astype(str).tolist(), reverse=True)
    ano_sel = col_f2.selectbox("Ano", anos_disp, key="hist_ano")

    # Aplica filtro
    df_l = df_l_all.copy()
    mes_int = meses_map.get(mes_sel)
    ano_int = int(ano_sel) if ano_sel != "Todos" else None

    if not df_l.empty:
        df_l["_dt"] = pd.to_datetime(df_l["Data"], dayfirst=True, errors="coerce")
        if mes_int:
            df_l = df_l[df_l["_dt"].dt.month == mes_int]
        if ano_int:
            df_l = df_l[df_l["_dt"].dt.year == ano_int]
        df_l = df_l.drop(columns=["_dt"]).reset_index(drop=True)

    # Coluna de status: "Com erros" ou "Pendente"
    ids_e = set(df_e["ID Bateria"].dropna().unique()) if not df_e.empty else set()
    if not df_l.empty:
        df_l["Status"] = df_l["ID Bateria"].apply(
            lambda x: "Com erros" if x in ids_e else "Pendente"
        )

    # ── Tabela paginada ────────────────────────────────────────────────────────
    total = len(df_l)
    if total == 0:
        st.info("Nenhum lancamento encontrado para o periodo selecionado.")
        return

    # Reseta a pagina quando o filtro muda
    filtro_atual = (mes_sel, ano_sel)
    if st.session_state.get("hist_filtro_anterior") != filtro_atual:
        st.session_state.hist_page = 0
        st.session_state.hist_filtro_anterior = filtro_atual

    if "hist_page" not in st.session_state:
        st.session_state.hist_page = 0

    total_pags = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(st.session_state.hist_page, total_pags - 1)
    df_page = df_l.iloc[page * PAGE_SIZE: page * PAGE_SIZE + PAGE_SIZE]

    st.caption(f"{total} registro(s)  |  Pagina {page + 1} de {total_pags}")

    st.dataframe(
        df_page[["ID Bateria", "Materia", "Data", "Acertos",
                 "Total", "Percentual", "Fonte", "Status"]],
        use_container_width=True,
        hide_index=True,
    )

    # Controles de paginacao
    col_ant, col_info, col_prox = st.columns([1, 3, 1])
    if col_ant.button("← Anterior", disabled=(page == 0), use_container_width=True):
        st.session_state.hist_page = page - 1
        st.rerun()
    if col_prox.button("Proximo →", disabled=(page >= total_pags - 1), use_container_width=True):
        st.session_state.hist_page = page + 1
        st.rerun()
