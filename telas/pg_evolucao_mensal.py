"""
pg_evolucao_mensal.py
Grafico de linha interativo: % de acertos por materia ao longo dos meses.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api_client import api_obter_evolucao
from telas.components import _injetar_css, page_title


def render():
    _injetar_css()
    page_title("Evolução Mensal", "% de acerto por matéria ao longo dos meses")

    pontos = api_obter_evolucao()

    if not pontos:
        st.info("Sem dados para exibir o gráfico.")
        return

    resumo = pd.DataFrame(pontos)  # columns: materia, mes, acertos, total, perc

    materias = sorted(resumo["materia"].unique())

    # ── Filtro de matérias ────────────────────────────────────────────────────
    selecionadas = st.multiselect(
        "Filtrar matérias",
        options=materias,
        default=materias[:10],  # limita padrão a 10 para não poluir
        key="evo_mat_filter",
    )
    if selecionadas:
        resumo = resumo[resumo["materia"].isin(selecionadas)]

    # ── Grafico Plotly ────────────────────────────────────────────────────────
    fig = go.Figure()

    for mat in sorted(resumo["materia"].unique()):
        sub = resumo[resumo["materia"] == mat].sort_values("mes")
        fig.add_trace(go.Scatter(
            x=sub["mes"],
            y=sub["perc"],
            mode="lines+markers",
            name=mat,
            hovertemplate=(
                f"<b>{mat}</b><br>"
                "Mês: %{x}<br>"
                "Acertos: %{y:.1f}%<extra></extra>"
            ),
        ))

    fig.add_hline(
        y=80, line_dash="dash", line_color="green",
        annotation_text="Meta 80%", annotation_position="right",
    )
    fig.add_hline(
        y=65, line_dash="dot", line_color="orange",
        annotation_text="Limite 65%", annotation_position="right",
    )

    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="% de Acertos",
        yaxis_range=[0, 108],
        legend_title="Matéria",
        hovermode="x unified",
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0a1628",
        font=dict(color="#c8d6e5"),
        xaxis=dict(gridcolor="#1a3050", linecolor="#1a3050", title_font=dict(color="#7a9ab8")),
        yaxis=dict(gridcolor="#1a3050", linecolor="#1a3050", title_font=dict(color="#7a9ab8")),
        legend=dict(bgcolor="#0d1b2a", bordercolor="#1a3050", borderwidth=1, font=dict(color="#c8d6e5")),
    )

    st.plotly_chart(fig, use_container_width=True)
