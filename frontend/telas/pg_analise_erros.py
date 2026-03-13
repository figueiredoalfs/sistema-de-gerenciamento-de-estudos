"""
frontend/telas/pg_analise_erros.py
Análise de padrões de erro: gráficos por tipo, tópico e evolução mensal.
Dados exclusivamente via API (sem database.py).
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from api_client import listar_erros

TIPO_LABEL = {
    "nao_sabia": "Não sabia",
    "confundiu": "Confundi",
    "esqueceu":  "Esqueci",
}
TIPO_COR = {
    "nao_sabia": "#e74c3c",
    "confundiu": "#f39c12",
    "esqueceu":  "#8ab0c8",
}
PLOT_LAYOUT = dict(
    paper_bgcolor="#111e2b",
    plot_bgcolor="#111e2b",
    font_color="#d0e4f0",
    margin=dict(t=30, b=10, l=10, r=10),
)


def _section(titulo: str):
    st.html(f"""
        <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
            padding:10px 18px;border-bottom:2px solid #00b4a6;margin-top:8px;">
            <span style="color:#fff;font-weight:700;font-size:0.82rem;
                letter-spacing:0.12em;text-transform:uppercase;">{titulo}</span>
        </div>
    """)


def render():
    st.html("""
        <div style="background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;
            text-align:center;border-bottom:3px solid #e74c3c;
            box-shadow:0 4px 16px rgba(0,0,0,0.35);">
            <span style="font-size:1.4rem;">&#128200;</span>
            <span style="color:#fff;font-weight:800;font-size:1.3rem;
                letter-spacing:0.12em;margin-left:10px;text-transform:uppercase;">
                Análise de Erros
            </span>
        </div>
    """)

    with st.spinner("Carregando erros..."):
        erros = listar_erros()

    if not erros:
        st.info("Nenhum erro registrado ainda.")
        return

    # Normaliza campos
    for e in erros:
        e["tipo"]     = TIPO_LABEL.get(e.get("observacao", ""), "Não sabia")
        e["qtd"]      = int(e.get("qtd_erros", 1))
        e["topico"]   = e.get("topico_texto") or "—"
        e["data_str"] = str(e.get("data", ""))[:7]  # "YYYY-MM"

    # ── Filtro de matéria ──────────────────────────────────────────────────────
    materias_disp = ["Todas"] + sorted({e.get("materia", "") for e in erros if e.get("materia")})
    col_f, _ = st.columns([2, 4])
    with col_f:
        st.caption("Filtrar por Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="ae_materia", label_visibility="collapsed")

    df_f    = erros if mat_sel == "Todas" else [e for e in erros if e.get("materia") == mat_sel]
    df_pend = [e for e in df_f if e.get("status") == "pendente"]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_e = sum(e["qtd"] for e in df_f)
    total_t = len({e["topico"] for e in df_f})
    total_m = len({e.get("materia", "") for e in df_f})
    total_r = sum(1 for e in df_f if e.get("status") == "resolvido")
    pct_res = int(total_r / len(df_f) * 100) if df_f else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Erros",    total_e)
    k2.metric("Tópicos Distintos", total_t)
    k3.metric("Matérias",          total_m)
    k4.metric("Resolvidos",        f"{pct_res}%")

    st.divider()

    # ── Gráfico 1: Top tópicos + Gráfico 2: Por tipo ─────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        _section("Top Tópicos com Mais Erros")
        from collections import Counter
        top_topicos = Counter()
        for e in df_pend:
            top_topicos[e["topico"]] += e["qtd"]
        top_items = top_topicos.most_common(15)[::-1]  # ordem crescente para barras horizontais

        if top_items:
            fig_bar = go.Figure(go.Bar(
                x=[v for _, v in top_items],
                y=[k for k, _ in top_items],
                orientation="h",
                marker_color="#e74c3c",
                text=[v for _, v in top_items],
                textposition="outside",
                textfont=dict(color="#d0e4f0", size=11),
            ))
            fig_bar.update_layout(
                **PLOT_LAYOUT,
                height=max(250, len(top_items) * 32),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, color="#7a9ab8"),
                yaxis=dict(showgrid=False, color="#d0e4f0", tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum erro pendente.")

    with col_right:
        _section("Distribuição por Tipo")
        tipo_count = Counter()
        for e in df_f:
            tipo_count[e["tipo"]] += e["qtd"]

        if tipo_count:
            tipos   = list(tipo_count.keys())
            valores = list(tipo_count.values())
            cores   = [TIPO_COR.get({v: k for k, v in TIPO_LABEL.items()}.get(t, ""), "#8ab0c8") for t in tipos]
            fig_pie = go.Figure(go.Pie(
                labels=tipos, values=valores, hole=0.45,
                marker=dict(colors=cores, line=dict(color="#111e2b", width=2)),
                textfont=dict(color="#d0e4f0", size=12),
            ))
            fig_pie.update_layout(**PLOT_LAYOUT, height=280, showlegend=True,
                                  legend=dict(font=dict(color="#d0e4f0")))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── Gráfico 3: Evolução temporal ──────────────────────────────────────────
    st.divider()
    _section("Evolução de Erros por Mês")

    erros_com_data = [e for e in df_f if e["data_str"]]
    if erros_com_data:
        from collections import defaultdict
        evo: dict = defaultdict(lambda: defaultdict(int))
        for e in erros_com_data:
            evo[e["data_str"]][e["tipo"]] += e["qtd"]

        rows = []
        for mes, tipos_dict in sorted(evo.items()):
            for tipo, qtd in tipos_dict.items():
                rows.append({"Mês": mes, "Tipo": tipo, "Qtd Erros": qtd})

        if rows:
            cores_tipo = {v: TIPO_COR.get(k, "#8ab0c8") for k, v in TIPO_LABEL.items()}
            fig_line = px.bar(
                rows, x="Mês", y="Qtd Erros", color="Tipo",
                color_discrete_map=cores_tipo, barmode="stack",
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

    # ── Tabela: erros por matéria (pendentes) ─────────────────────────────────
    st.divider()
    _section("Erros por Matéria (pendentes)")
    from collections import Counter as C2
    por_mat = C2()
    for e in df_pend:
        por_mat[e.get("materia", "—")] += e["qtd"]
    por_mat_sorted = por_mat.most_common()

    if por_mat_sorted:
        th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
              "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;")
        rows = ""
        for i, (mat, qtd) in enumerate(por_mat_sorted):
            bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"
            rows += (f'<tr style="background:{bg};border-bottom:1px solid #1a3050;">'
                     f'<td style="padding:10px 14px;color:#fff;font-weight:700;">{mat}</td>'
                     f'<td style="padding:10px 14px;text-align:center;'
                     f'color:#e74c3c;font-weight:800;">{qtd}</td></tr>')
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
