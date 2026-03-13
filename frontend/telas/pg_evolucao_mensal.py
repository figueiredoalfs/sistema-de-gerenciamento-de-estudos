"""
frontend/telas/pg_evolucao_mensal.py
Gráfico de evolução mensal do % de acertos por matéria.
Dados exclusivamente via API (sem database.py).

Estratégia: chama GET /desempenho?mes=X&ano=Y para os últimos N meses
e agrega os resultados em um DataFrame para o gráfico.
"""

import datetime
import streamlit as st
import plotly.graph_objects as go
from api_client import obter_desempenho

_MESES_HISTORICO = 9  # quantos meses retroativos buscar


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_mes(token: str, mes: int, ano: int) -> dict | None:
    """Busca desempenho de um mês específico (cacheado 5 min)."""
    return obter_desempenho(mes=mes, ano=ano)


def _ultimos_meses(n: int) -> list[tuple[int, int]]:
    """Retorna lista de (mes, ano) dos últimos n meses, do mais antigo ao mais recente."""
    hoje = datetime.date.today()
    meses = []
    for i in range(n - 1, -1, -1):
        d = hoje.replace(day=1) - datetime.timedelta(days=1) * (i * 30)
        meses.append((d.month, d.year))
    # Remove duplicatas preservando ordem
    seen = set()
    result = []
    for m in meses:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


def render():
    st.html("""
        <div style="background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;
            text-align:center;border-bottom:3px solid #00b4a6;
            box-shadow:0 4px 16px rgba(0,0,0,0.35);">
            <span style="font-size:1.4rem;">&#128200;</span>
            <span style="color:#ffffff;font-weight:800;font-size:1.3rem;
                letter-spacing:0.12em;margin-left:10px;text-transform:uppercase;">
                Evolução Mensal por Matéria
            </span>
        </div>
    """)

    token = st.session_state.get("api_token", "")
    periodos = _ultimos_meses(_MESES_HISTORICO)

    # Coleta dados mês a mês
    dados_mensais: list[dict] = []
    with st.spinner(f"Carregando evolução dos últimos {_MESES_HISTORICO} meses..."):
        for mes, ano in periodos:
            dados = _fetch_mes(token, mes, ano)
            if dados and dados.get("por_materia"):
                mes_label = f"{ano}-{mes:02d}"
                for item in dados["por_materia"]:
                    dados_mensais.append({
                        "Mes":     mes_label,
                        "Materia": item["materia"],
                        "Perc":    float(item["perc"]),
                    })

    if not dados_mensais:
        st.info("Sem dados para exibir o gráfico. Lance baterias para ver sua evolução.")
        return

    # Agrupa por Matéria
    from collections import defaultdict
    por_materia: dict = defaultdict(list)
    for row in dados_mensais:
        por_materia[row["Materia"]].append((row["Mes"], row["Perc"]))

    # Ordena cada matéria por mês
    for mat in por_materia:
        por_materia[mat].sort(key=lambda x: x[0])

    # ── Gráfico Plotly ────────────────────────────────────────────────────────
    fig = go.Figure()
    for mat, pontos in sorted(por_materia.items()):
        meses  = [p[0] for p in pontos]
        percs  = [p[1] for p in pontos]
        fig.add_trace(go.Scatter(
            x=meses, y=percs,
            mode="lines+markers",
            name=mat,
            hovertemplate=(
                f"<b>{mat}</b><br>Mês: %{{x}}<br>Acertos: %{{y:.1f}}%<extra></extra>"
            ),
        ))

    fig.add_hline(y=80, line_dash="dash",  line_color="green",
                  annotation_text="Meta 80%",   annotation_position="right")
    fig.add_hline(y=65, line_dash="dot",   line_color="orange",
                  annotation_text="Limite 65%", annotation_position="right")

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
        legend=dict(bgcolor="#0d1b2a", bordercolor="#1a3050", borderwidth=1,
                    font=dict(color="#c8d6e5")),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Dados dos últimos {_MESES_HISTORICO} meses. Atualizado a cada 5 minutos.")
