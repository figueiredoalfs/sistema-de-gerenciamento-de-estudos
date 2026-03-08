"""
pg_evolucao_mensal.py
Grafico de linha interativo: % de acertos por materia ao longo dos meses.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import ler_lancamentos


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
            <span style="font-size:1.4rem;">&#128200;</span>
            <span style="
                color:#ffffff;
                font-weight:800;
                font-size:1.3rem;
                letter-spacing:0.12em;
                margin-left:10px;
                text-transform:uppercase;
            ">EVOLUCAO MENSAL POR MATERIA</span>
        </div>
    """)

    df = ler_lancamentos(st.session_state.usuario["id"])

    if df.empty:
        st.info("Sem dados para exibir o grafico.")
        return

    # Agrupa por mes e materia
    df = df.copy()
    df["_dt"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["_dt"])
    df["Mes"] = df["_dt"].dt.to_period("M").astype(str)

    resumo = (
        df.groupby(["Mes", "Materia"])
        .agg(Acertos=("Acertos", "sum"), Total=("Total", "sum"))
        .reset_index()
    )
    resumo["Perc"] = (resumo["Acertos"] / resumo["Total"] * 100).fillna(0).round(1)

    materias = sorted(resumo["Materia"].unique())

    # ── Grafico Plotly ────────────────────────────────────────────────────────
    fig = go.Figure()

    for mat in materias:
        sub = resumo[resumo["Materia"] == mat].sort_values("Mes")
        fig.add_trace(go.Scatter(
            x=sub["Mes"],
            y=sub["Perc"],
            mode="lines+markers",
            name=mat,
            hovertemplate=(
                f"<b>{mat}</b><br>"
                "Mes: %{x}<br>"
                "Acertos: %{y:.1f}%<extra></extra>"
            ),
        ))

    # Linhas de referencia de desempenho
    fig.add_hline(
        y=80, line_dash="dash", line_color="green",
        annotation_text="Meta 80%", annotation_position="right",
    )
    fig.add_hline(
        y=65, line_dash="dot", line_color="orange",
        annotation_text="Limite 65%", annotation_position="right",
    )

    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="% de Acertos",
        yaxis_range=[0, 108],
        legend_title="Materia",
        hovermode="x unified",
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0a1628",
        font=dict(color="#c8d6e5"),
        xaxis=dict(gridcolor="#1a3050", linecolor="#1a3050", title_font=dict(color="#7a9ab8")),
        yaxis=dict(gridcolor="#1a3050", linecolor="#1a3050", title_font=dict(color="#7a9ab8")),
        legend=dict(bgcolor="#0d1b2a", bordercolor="#1a3050", borderwidth=1, font=dict(color="#c8d6e5")),
    )

    st.plotly_chart(fig, use_container_width=True)
