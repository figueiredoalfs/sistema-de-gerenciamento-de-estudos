"""
frontend/telas/pg_desempenho.py
Painel de desempenho por matéria.
Dados exclusivamente via API (sem database.py).
"""

import datetime
import streamlit as st
from api_client import obter_desempenho

_FONTES_OPCOES = {
    "qconcursos":                 "Banco de Questões (Qconcursos/TEC/Gran)",
    "tec":                        "TEC Concursos",
    "prova_anterior_mesma_banca": "Prova Original — mesma banca",
    "prova_anterior_outra_banca": "Prova Original — outra banca",
    "simulado":                   "Simulado",
    "quiz_ia":                    "Quiz IA",
    "manual":                     "Manual / Mentoria",
    "curso":                      "Curso Online",
    "calibracao":                 "Calibração",
}


def _perc_color(perc: float) -> str:
    if perc > 85:   return "#4ade80"
    elif perc >= 75: return "#27ae60"
    elif perc >= 65: return "#f39c12"
    return "#e74c3c"


def _status(perc: float):
    if perc > 85:    return "#4ade80", "&#9679;", "Dominando"
    elif perc >= 75: return "#27ae60", "&#9679;", "Meta"
    elif perc >= 65: return "#f39c12", "&#9679;", "Atenção"
    return "#e74c3c", "&#9679;", "Crítico"


def _prioridade(perc: float):
    if perc > 85:    return "#4ade80", "&#9989;",  "Dominando o Assunto"
    elif perc >= 75: return "#27ae60", "&#128218;", "Zona de Classificação"
    elif perc >= 65: return "#f39c12", "&#128203;", "Moderada"
    return "#e74c3c", "&#128680;", "URGENTE"


def _tend_from_api(tend_atual, tend_ant):
    if tend_atual is None or tend_ant is None:
        return "&rarr;", "Estável", "#7a9ab8"
    diff = tend_atual - tend_ant
    if diff > 1:    return "&#9650;", "Subindo", "#00b4a6"
    elif diff < -1: return "&#9660;", "Caindo",  "#e74c3c"
    return "&rarr;", "Estável", "#7a9ab8"


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_desempenho(token: str, mes, ano, fontes_tuple) -> dict | None:
    """Cache por token + filtros. Invalida a cada 60 segundos."""
    fontes = list(fontes_tuple) if fontes_tuple else None
    return obter_desempenho(mes=mes, ano=ano, fontes=fontes)


def _render_tabela(por_materia: list):
    st.html("""
        <div style="background:#0d1b2a;border-radius:8px 8px 0 0;padding:10px 18px;
            border-bottom:2px solid #00b4a6;">
            <span style="color:#ffffff;font-weight:700;font-size:0.82rem;
                letter-spacing:0.12em;text-transform:uppercase;">DESEMPENHO POR MATÉRIA</span>
        </div>
    """)

    if not por_materia:
        st.info("Nenhum dado disponível para os filtros selecionados.")
        return

    cols_header = ["MATÉRIA", "REALIZADAS", "ACERTOS", "% ACERTO", "TENDÊNCIA", "STATUS", "PRIORIDADE"]
    th_style = ("padding:10px 14px;text-align:center;font-size:0.71rem;"
                "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(f'<th style="{th_style}">{h}</th>' for h in cols_header)

    rows_html = ""
    for i, item in enumerate(por_materia):
        mat        = item["materia"]
        realizadas = item["realizadas"]
        acertos    = item["acertos"]
        perc_mat   = item["perc"]
        seta, tend_txt, tend_cor = _tend_from_api(item.get("tend_perc_atual"), item.get("tend_perc_anterior"))

        perc_cor                 = _perc_color(perc_mat)
        st_cor, st_icone, st_txt = _status(perc_mat)
        pr_cor, pr_icone, pr_txt = _prioridade(perc_mat)
        row_bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        td = "padding:10px 14px;text-align:center;white-space:nowrap;"

        rows_html += f"""
        <tr style="background:{row_bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:800;color:#ffffff;font-size:0.9rem;">{mat}</td>
            <td style="{td}color:#c8d6e5;">{realizadas}</td>
            <td style="{td}color:#c8d6e5;">{acertos}</td>
            <td style="{td}font-weight:700;color:{perc_cor};font-size:0.95rem;">{perc_mat}%</td>
            <td style="{td}font-weight:600;color:{tend_cor};">{seta}&nbsp;{tend_txt}</td>
            <td style="{td}">
                <span style="color:{st_cor};font-size:0.85rem;">{st_icone}</span>
                <span style="color:#c8d6e5;margin-left:4px;">{st_txt}</span>
            </td>
            <td style="{td}font-weight:700;color:{pr_cor};">{pr_icone}&nbsp;{pr_txt}</td>
        </tr>
        """

    st.html(f"""
        <div style="background:#0d1b2a;border-radius:0 0 8px 8px;overflow:hidden;
            border:1px solid #1a3050;border-top:none;
            box-shadow:0 6px 20px rgba(0,0,0,0.4);margin-bottom:20px;">
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:#061020;">{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """)


def render():
    st.html("""
        <div style="background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;text-align:center;
            border-bottom:3px solid #00b4a6;box-shadow:0 4px 16px rgba(0,0,0,0.35);">
            <span style="font-size:1.4rem;">&#127942;</span>
            <span style="color:#ffffff;font-weight:800;font-size:1.3rem;
                letter-spacing:0.12em;margin-left:10px;text-transform:uppercase;">
                Painel de Desempenho
            </span>
        </div>
    """)

    # ── Filtros ────────────────────────────────────────────────────────────────
    meses_map = {
        "Geral": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
        "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
        "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
    }
    ano_atual = datetime.date.today().year
    anos_opts = ["Todos"] + [str(a) for a in range(ano_atual, ano_atual - 4, -1)]

    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

    with col_f1:
        st.caption("Mês")
        mes_sel = st.selectbox("Mês", list(meses_map.keys()), key="dash_mes",
                               label_visibility="collapsed")
    with col_f2:
        st.caption("Ano")
        ano_sel = st.selectbox("Ano", anos_opts, key="dash_ano",
                               label_visibility="collapsed")
    with col_f3:
        st.caption("Fonte das Questões")
        fonte_labels = st.multiselect(
            "Fonte", list(_FONTES_OPCOES.values()), key="dash_fonte",
            placeholder="Todas as fontes", label_visibility="collapsed",
        )
        label_to_slug = {v: k for k, v in _FONTES_OPCOES.items()}
        fonte_slugs   = [label_to_slug[l] for l in fonte_labels if l in label_to_slug]

    mes_int  = meses_map.get(mes_sel)
    ano_int  = int(ano_sel) if ano_sel != "Todos" else None
    token    = st.session_state.get("api_token", "")

    # Busca dados da API com os filtros selecionados
    with st.spinner("Carregando desempenho..."):
        dados = _fetch_desempenho(token, mes_int, ano_int, tuple(fonte_slugs))

    if dados is None:
        st.error("Não foi possível carregar dados de desempenho. Verifique se o servidor está disponível.")
        return

    total_q    = dados.get("total_questoes", 0)
    total_a    = dados.get("total_acertos", 0)
    perc_geral = dados.get("perc_geral", 0.0)

    k1, k2 = st.columns(2)
    k1.metric("Total de Questões", total_q)
    k2.metric("Acertos", f"{total_a}  ({perc_geral:.1f}%)")

    st.divider()
    _render_tabela(dados.get("por_materia", []))
