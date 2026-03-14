"""
pg_analise_erros.py
Análise de padrões de erro: gráficos, dimensão temporal e breakdown por tipo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import ler_erros
from telas.components import page_title, _injetar_css

TIPO_LABEL = {
    "nao_sabia":  "Não sabia",
    "confundiu":  "Confundi",
    "esqueceu":   "Esqueci",
}
TIPO_COR = {
    "nao_sabia":  "#e74c3c",
    "confundiu":  "#f39c12",
    "esqueceu":   "#8ab0c8",
}
PLOT_LAYOUT = dict(
    paper_bgcolor="#111e2b",
    plot_bgcolor="#111e2b",
    font_color="#d0e4f0",
    margin=dict(t=30, b=10, l=10, r=10),
)


def _header():
    _injetar_css()
    page_title("Análise de Erros", "Padrões e tendências dos seus erros por matéria")


def _section(titulo: str):
    st.html(f"""
        <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
            padding:10px 18px;border-bottom:2px solid #00b4a6;margin-top:8px;">
            <span style="color:#fff;font-weight:700;font-size:0.82rem;
                letter-spacing:0.12em;text-transform:uppercase;">{titulo}</span>
        </div>
    """)


def render():
    _header()

    uid = st.session_state.usuario["id"]
    df  = ler_erros(uid)

    if df.empty:
        st.info("Nenhum erro registrado ainda.")
        return

    # Normaliza tipo para legível
    df["Tipo"] = df["Tipo Erro"].map(TIPO_LABEL).fillna("Não sabia")

    # ── Filtro de matéria ──────────────────────────────────────────────────────
    materias_disp = ["Todas"] + sorted(df["Materia"].dropna().unique().tolist())
    col_f, _ = st.columns([2, 4])
    with col_f:
        st.caption("Filtrar por Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="ae_materia",
                               label_visibility="collapsed")

    df_f = df if mat_sel == "Todas" else df[df["Materia"] == mat_sel]
    df_pend = df_f[df_f["Status"] == "pendente"]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_e = int(df_f["Qtd Erros"].sum())
    total_t = df_f["Topico"].nunique()
    total_m = df_f["Materia"].nunique()
    pct_res = int((df_f["Status"] == "revisado").sum() / len(df_f) * 100) if len(df_f) > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Erros",    total_e)
    k2.metric("Tópicos Distintos", total_t)
    k3.metric("Matérias",          total_m)
    k4.metric("Revisados",         f"{pct_res}%")

    st.divider()

    # ── Gráfico 1: Top tópicos (barras horizontais) + Gráfico 2: Por tipo ────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        _section("Top Tópicos com Mais Erros")
        ranking = (
            df_pend.groupby("Topico")["Qtd Erros"]
            .sum().sort_values(ascending=True).tail(15).reset_index()
        )
        if not ranking.empty:
            fig_bar = go.Figure(go.Bar(
                x=ranking["Qtd Erros"],
                y=ranking["Topico"],
                orientation="h",
                marker_color="#e74c3c",
                text=ranking["Qtd Erros"],
                textposition="outside",
                textfont=dict(color="#d0e4f0", size=11),
            ))
            fig_bar.update_layout(
                **PLOT_LAYOUT,
                height=max(250, len(ranking) * 32),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                           color="#7a9ab8"),
                yaxis=dict(showgrid=False, color="#d0e4f0", tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum erro pendente.")

    with col_right:
        _section("Distribuição por Tipo")
        por_tipo = (
            df_f.groupby("Tipo")["Qtd Erros"].sum().reset_index()
        )
        if not por_tipo.empty:
            cores = [TIPO_COR.get(
                {v: k for k, v in TIPO_LABEL.items()}.get(t, ""), "#8ab0c8"
            ) for t in por_tipo["Tipo"]]
            fig_pie = go.Figure(go.Pie(
                labels=por_tipo["Tipo"],
                values=por_tipo["Qtd Erros"],
                hole=0.45,
                marker=dict(colors=cores,
                            line=dict(color="#111e2b", width=2)),
                textfont=dict(color="#d0e4f0", size=12),
            ))
            fig_pie.update_layout(**PLOT_LAYOUT, height=280,
                                  showlegend=True,
                                  legend=dict(font=dict(color="#d0e4f0")))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── Gráfico 3: Evolução temporal de erros por mês ─────────────────────────
    st.divider()
    _section("Evolução de Erros por Mês")

    df_dt = df_f.copy()
    df_dt["_dt"] = pd.to_datetime(df_dt["Data"], dayfirst=True, errors="coerce")
    df_dt = df_dt.dropna(subset=["_dt"])

    if not df_dt.empty:
        df_dt["Mês"] = df_dt["_dt"].dt.to_period("M").astype(str)
        evo = (
            df_dt.groupby(["Mês", "Tipo"])["Qtd Erros"]
            .sum().reset_index()
            .sort_values("Mês")
        )
        cores_tipo = {v: TIPO_COR.get(k, "#8ab0c8") for k, v in TIPO_LABEL.items()}
        fig_line = px.bar(
            evo, x="Mês", y="Qtd Erros", color="Tipo",
            color_discrete_map=cores_tipo,
            barmode="stack",
        )
        fig_line.update_layout(
            **PLOT_LAYOUT, height=280,
            xaxis=dict(showgrid=False, color="#7a9ab8"),
            yaxis=dict(showgrid=True, gridcolor="#1a3050", color="#7a9ab8"),
            legend=dict(font=dict(color="#d0e4f0")),
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Sem dados com data para exibir evolução.")

    # ── Tabela: erros por matéria ─────────────────────────────────────────────
    st.divider()
    _section("Erros por Matéria (pendentes)")
    por_mat = (
        df_pend.groupby("Materia")["Qtd Erros"]
        .sum().sort_values(ascending=False).reset_index()
    )
    if not por_mat.empty:
        th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
              "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;")
        rows = ""
        for i, row in por_mat.iterrows():
            bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"
            rows += (f'<tr style="background:{bg};border-bottom:1px solid #1a3050;">'
                     f'<td style="padding:10px 14px;color:#fff;font-weight:700;">{row["Materia"]}</td>'
                     f'<td style="padding:10px 14px;text-align:center;'
                     f'color:#e74c3c;font-weight:800;">{int(row["Qtd Erros"])}</td>'
                     f'</tr>')
        st.html(f"""
            <div style="background:#0d1b2a;border-radius:0 0 8px 8px;overflow:hidden;
                border:1px solid #1a3050;border-top:none;margin-bottom:20px;">
                <table style="width:100%;border-collapse:collapse;">
                    <thead><tr style="background:#061020;">
                        <th style="{th}">MATÉRIA</th>
                        <th style="{th}text-align:center;">ERROS PENDENTES</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        """)
    else:
        st.success("Nenhum erro pendente para os filtros selecionados.")
