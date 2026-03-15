"""
pg_historico.py
Histórico paginado de baterias com filtros de período, matéria e % colorida.
"""

import pandas as pd
import streamlit as st

from api_client import api_listar_baterias
from telas.components import _injetar_css, page_title

PAGE_SIZE = 20


def _perc_color(p: float) -> str:
    if p >= 85: return "#4ade80"
    if p >= 75: return "#27ae60"
    if p >= 65: return "#f39c12"
    return "#e74c3c"


def render():
    _injetar_css()
    page_title("Histórico de Baterias", "Registro completo de todas as sessões lançadas")

    baterias = api_listar_baterias(por_pagina=200)

    if not baterias:
        st.info("Nenhum lançamento registrado ainda.")
        return

    df_all = pd.DataFrame(baterias)
    df_all["data_dt"] = pd.to_datetime(df_all["data"], errors="coerce")
    df_all["Data"]    = df_all["data_dt"].dt.strftime("%d/%m/%Y")

    # ── Filtros ───────────────────────────────────────────────────────────────
    meses_map = {
        "Todos": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
        "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
        "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
    }

    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

    with col_f1:
        st.caption("Mês")
        mes_sel = st.selectbox("Mês", list(meses_map.keys()), key="hist_mes",
                               label_visibility="collapsed")
    with col_f2:
        anos_disp = ["Todos"] + sorted(
            df_all["data_dt"].dropna().dt.year.unique().astype(str).tolist(), reverse=True
        )
        st.caption("Ano")
        ano_sel = st.selectbox("Ano", anos_disp, key="hist_ano",
                               label_visibility="collapsed")
    with col_f3:
        todas_materias = sorted({m for mats in df_all["materias"] for m in mats if m})
        materias_disp  = ["Todas"] + todas_materias
        st.caption("Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="hist_mat",
                               label_visibility="collapsed")

    # Aplica filtros
    df = df_all.copy()
    mes_int = meses_map.get(mes_sel)
    ano_int = int(ano_sel) if ano_sel != "Todos" else None
    if mes_int:
        df = df[df["data_dt"].dt.month == mes_int]
    if ano_int:
        df = df[df["data_dt"].dt.year == ano_int]
    if mat_sel != "Todas":
        df = df[df["materias"].apply(lambda ms: mat_sel in ms)]
    df = df.reset_index(drop=True)

    if df.empty:
        st.info("Nenhum lançamento encontrado para os filtros selecionados.")
        return

    # ── Paginação ──────────────────────────────────────────────────────────────
    total = len(df)
    filtro_atual = (mes_sel, ano_sel, mat_sel)
    if st.session_state.get("hist_filtro_ant") != filtro_atual:
        st.session_state.hist_page = 0
        st.session_state.hist_filtro_ant = filtro_atual
    if "hist_page" not in st.session_state:
        st.session_state.hist_page = 0

    total_pags = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page       = min(st.session_state.hist_page, total_pags - 1)
    df_page    = df.iloc[page * PAGE_SIZE: page * PAGE_SIZE + PAGE_SIZE]

    st.caption(f"{total} bateria(s) · Página {page + 1} de {total_pags}")

    # ── Tabela estilizada ──────────────────────────────────────────────────────
    th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
          "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(
        f'<th style="{th}">{c}</th>'
        for c in ["ID BATERIA", "MATÉRIAS", "DATA", "ACERTOS", "TOTAL", "%"]
    )

    rows_html = ""
    for i, row in df_page.iterrows():
        perc = float(row.get("percentual_geral") or 0.0)
        cor  = _perc_color(perc)
        bg   = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        td   = "padding:10px 14px;vertical-align:middle;white-space:nowrap;"
        mats_str = ", ".join(sorted(row["materias"])) if row["materias"] else "—"
        bid_short = str(row["bateria_id"])[:8] + "…"

        rows_html += f"""
        <tr style="background:{bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:700;color:#00b4a6;" title="{row['bateria_id']}">{bid_short}</td>
            <td style="{td}color:#fff;font-size:0.82rem;">{mats_str}</td>
            <td style="{td}color:#8ab0c8;">{row['Data']}</td>
            <td style="{td}color:#c8d6e5;text-align:center;">{int(row['total_acertos'])}</td>
            <td style="{td}color:#c8d6e5;text-align:center;">{int(row['total_questoes'])}</td>
            <td style="{td}font-weight:800;color:{cor};text-align:center;">{perc:.1f}%</td>
        </tr>"""

    st.html(f"""
        <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
            padding:10px 18px;border-bottom:2px solid #00b4a6;">
            <span style="color:#fff;font-weight:700;font-size:0.82rem;
                letter-spacing:0.12em;text-transform:uppercase;">Lançamentos</span>
        </div>
        <div style="background:#0d1b2a;border-radius:0 0 8px 8px;overflow:hidden;
            border:1px solid #1a3050;border-top:none;
            box-shadow:0 6px 20px rgba(0,0,0,0.4);margin-bottom:16px;">
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:#061020;">{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """)

    # ── Controles de paginação ────────────────────────────────────────────────
    col_ant, _col_info, col_prox = st.columns([1, 3, 1])
    if col_ant.button("← Anterior", disabled=(page == 0), use_container_width=True):
        st.session_state.hist_page = page - 1
        st.rerun()
    if col_prox.button("Próximo →", disabled=(page >= total_pags - 1), use_container_width=True):
        st.session_state.hist_page = page + 1
        st.rerun()
