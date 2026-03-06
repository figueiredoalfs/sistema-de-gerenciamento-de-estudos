"""
pg_analise_erros.py
Analise detalhada de erros: ranking por topico, distribuicao por materia e tabela completa.
"""

import streamlit as st
import pandas as pd
from database import ler_erros


def _dark_section(titulo: str):
    st.html(f"""
        <div style="
            background:#0d1b2a;
            border-radius:8px 8px 0 0;
            padding:10px 18px;
            border-bottom:2px solid #00b4a6;
            margin-top:8px;
        ">
            <span style="
                color:#ffffff;
                font-weight:700;
                font-size:0.82rem;
                letter-spacing:0.12em;
                text-transform:uppercase;
            ">{titulo}</span>
        </div>
    """)


def _tabela_dark(df: pd.DataFrame, cols: list, col_destaque: str = None):
    """Renderiza um DataFrame como tabela HTML no tema dark."""
    th_style = (
        "padding:10px 14px;"
        "text-align:center;"
        "font-size:0.71rem;"
        "letter-spacing:0.08em;"
        "color:#7a9ab8;"
        "font-weight:600;"
        "white-space:nowrap;"
    )
    header_html = "".join(f'<th style="{th_style}">{c.upper()}</th>' for c in cols)

    rows_html = ""
    for i, row in df[cols].iterrows():
        row_bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        tds = ""
        for c in cols:
            val = row[c]
            td_style = "padding:10px 14px;text-align:center;white-space:nowrap;color:#c8d6e5;"
            if c == col_destaque:
                td_style += "font-weight:700;color:#e74c3c;"
            elif i == 0 and c == cols[0]:
                td_style += "font-weight:800;color:#ffffff;"
            tds += f'<td style="{td_style}">{val}</td>'
        rows_html += f'<tr style="background:{row_bg};border-bottom:1px solid #1a3050;">{tds}</tr>'

    st.html(f"""
        <div style="
            background:#0d1b2a;
            border-radius:0 0 8px 8px;
            overflow:hidden;
            border:1px solid #1a3050;
            border-top:none;
            box-shadow:0 6px 20px rgba(0,0,0,0.4);
            margin-bottom:20px;
        ">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="background:#061020;">{header_html}</tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """)


def render():
    df = ler_erros()

    # Header
    st.html("""
        <div style="
            background: linear-gradient(135deg, #061020 0%, #0d1b2a 100%);
            border-radius: 10px;
            padding: 18px 24px;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #e74c3c;
            box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        ">
            <span style="font-size:1.4rem;">&#128680;</span>
            <span style="
                color:#ffffff;
                font-weight:800;
                font-size:1.3rem;
                letter-spacing:0.12em;
                margin-left:10px;
                text-transform:uppercase;
            ">ANALISE DE ERROS</span>
        </div>
    """)

    if df.empty:
        st.info("Nenhum erro registrado ainda.")
        return

    # ── Filtro de materia ──────────────────────────────────────────────────────
    materias_disp = ["Todas"] + sorted(df["Materia"].dropna().unique().tolist())
    col_f1, _ = st.columns([2, 4])
    with col_f1:
        st.caption("Filtrar por Materia")
        mat_sel = st.selectbox("Materia", materias_disp, key="ae_materia",
                               label_visibility="collapsed")

    df_f = df if mat_sel == "Todas" else df[df["Materia"] == mat_sel]

    # KPIs
    total_e = int(df_f["Qtd Erros"].sum())
    total_t = df_f["Topico"].nunique()
    total_m = df_f["Materia"].nunique()

    k1, k2, k3 = st.columns(3)
    k1.metric("Total de Erros", total_e)
    k2.metric("Topicos Distintos", total_t)
    k3.metric("Materias", total_m)

    st.divider()

    col_left, col_right = st.columns([3, 2])

    # ── Top Erros por Topico ───────────────────────────────────────────────────
    with col_left:
        _dark_section("Top Erros por Topico")
        ranking = (
            df_f.groupby("Topico")["Qtd Erros"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
        )
        ranking.index = ranking.index + 1
        _tabela_dark(ranking.reset_index().rename(columns={"index": "#"}),
                     ["#", "Topico", "Qtd Erros"], col_destaque="Qtd Erros")

    # ── Erros por Materia ─────────────────────────────────────────────────────
    with col_right:
        _dark_section("Erros por Materia")
        por_mat = (
            df_f.groupby("Materia")["Qtd Erros"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        _tabela_dark(por_mat, ["Materia", "Qtd Erros"], col_destaque="Qtd Erros")

    # ── Tabela completa ────────────────────────────────────────────────────────
    with st.expander("Ver todos os registros de erros"):
        st.dataframe(
            df_f[["Materia", "Topico", "Qtd Erros", "Data", "Observacao", "Providencia"]]
            .sort_values("Qtd Erros", ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
