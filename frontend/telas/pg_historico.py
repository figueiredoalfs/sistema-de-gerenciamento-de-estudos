"""
frontend/telas/pg_historico.py
Histórico de baterias paginado.
Dados exclusivamente via API (sem database.py).

Nota: A API retorna BateriaResumo (1 linha por bateria, não por matéria).
"""

import streamlit as st
from api_client import listar_baterias, listar_erros

PAGE_SIZE = 20


def _perc_color(p: float) -> str:
    if p >= 85: return "#4ade80"
    if p >= 75: return "#27ae60"
    if p >= 65: return "#f39c12"
    return "#e74c3c"


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_baterias(token: str) -> list:
    return listar_baterias(por_pagina=200)


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_erros_ids(token: str) -> set:
    erros = listar_erros()
    return {e.get("id_bateria") for e in erros if e.get("id_bateria")}


def render():
    st.html("""
        <div style="background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;
            text-align:center;border-bottom:3px solid #00b4a6;
            box-shadow:0 4px 16px rgba(0,0,0,0.35);">
            <span style="font-size:1.4rem;">&#128203;</span>
            <span style="color:#fff;font-weight:800;font-size:1.3rem;
                letter-spacing:0.12em;margin-left:10px;text-transform:uppercase;">
                Histórico de Baterias
            </span>
        </div>
    """)

    token = st.session_state.get("api_token", "")

    with st.spinner("Carregando histórico..."):
        baterias = _fetch_baterias(token)
        ids_com_erros = _fetch_erros_ids(token)

    if not baterias:
        st.info("Nenhum lançamento registrado ainda.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    # Extrai anos disponíveis das baterias
    anos_set = set()
    for b in baterias:
        data_str = str(b.get("data", ""))
        if data_str:
            ano = data_str[:4]
            if ano.isdigit():
                anos_set.add(ano)
    anos_disp = ["Todos"] + sorted(anos_set, reverse=True)

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        st.caption("Ano")
        ano_sel = st.selectbox("Ano", anos_disp, key="hist_ano", label_visibility="collapsed")
    with col_f2:
        st.caption("Com Erros")
        erros_sel = st.selectbox("Com Erros", ["Todos", "Sim", "Não"], key="hist_erros",
                                 label_visibility="collapsed")

    # Aplica filtros
    filtradas = baterias
    if ano_sel != "Todos":
        filtradas = [b for b in filtradas if str(b.get("data", "")).startswith(ano_sel)]
    if erros_sel == "Sim":
        filtradas = [b for b in filtradas if b.get("bateria_id") in ids_com_erros]
    elif erros_sel == "Não":
        filtradas = [b for b in filtradas if b.get("bateria_id") not in ids_com_erros]

    if not filtradas:
        st.info("Nenhum registro encontrado para os filtros selecionados.")
        return

    # ── Paginação ──────────────────────────────────────────────────────────────
    total      = len(filtradas)
    filtro_key = (ano_sel, erros_sel)
    if st.session_state.get("hist_filtro_ant") != filtro_key:
        st.session_state.hist_page    = 0
        st.session_state.hist_filtro_ant = filtro_key
    if "hist_page" not in st.session_state:
        st.session_state.hist_page = 0

    total_pags = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page       = min(st.session_state.hist_page, total_pags - 1)
    pagina_bat = filtradas[page * PAGE_SIZE: page * PAGE_SIZE + PAGE_SIZE]

    st.caption(f"{total} bateria(s) · Página {page + 1} de {total_pags}")

    # ── Tabela estilizada ──────────────────────────────────────────────────────
    th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
          "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(
        f'<th style="{th}">{c}</th>'
        for c in ["ID BATERIA", "DATA", "TOTAL", "ACERTOS", "%", "MATÉRIAS", "ERROS"]
    )

    rows_html = ""
    for i, b in enumerate(pagina_bat):
        bid     = b.get("bateria_id", "—")
        data    = str(b.get("data", "—"))[:19].replace("T", " ")
        total_q = b.get("total_questoes", 0)
        acertos = b.get("total_acertos", 0)
        perc    = float(b.get("percentual_geral", 0))
        mats    = ", ".join(b.get("materias", []))[:60]
        cor     = _perc_color(perc)
        bg      = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        com_err = bid in ids_com_erros
        err_cor = "#e74c3c" if com_err else "#4ade80"
        err_txt = "Sim" if com_err else "Não"
        td = "padding:10px 14px;vertical-align:middle;white-space:nowrap;"

        rows_html += f"""
        <tr style="background:{bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:700;color:#00b4a6;">{bid[:20]}</td>
            <td style="{td}color:#8ab0c8;">{data}</td>
            <td style="{td}color:#c8d6e5;text-align:center;">{total_q}</td>
            <td style="{td}color:#c8d6e5;text-align:center;">{acertos}</td>
            <td style="{td}font-weight:800;color:{cor};text-align:center;">{perc:.1f}%</td>
            <td style="{td}color:#c8d6e5;font-size:0.82rem;white-space:normal;">{mats or '—'}</td>
            <td style="{td}text-align:center;">
                <span style="color:{err_cor};font-weight:700;font-size:0.82rem;">{err_txt}</span>
            </td>
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

    # Controles de paginação
    col_ant, col_info, col_prox = st.columns([1, 3, 1])
    if col_ant.button("← Anterior", disabled=(page == 0), use_container_width=True):
        st.session_state.hist_page = page - 1
        st.rerun()
    if col_prox.button("Próximo →", disabled=(page >= total_pags - 1), use_container_width=True):
        st.session_state.hist_page = page + 1
        st.rerun()
