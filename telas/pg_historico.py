"""
pg_historico.py
Histórico paginado de baterias com filtros de período, matéria e % colorida.
"""

import streamlit as st
import pandas as pd
from database import ler_lancamentos, ler_erros
from telas.components import page_title, _injetar_css

PAGE_SIZE = 20


def _perc_color(p: float) -> str:
    if p >= 85: return "#4ade80"
    if p >= 75: return "#27ae60"
    if p >= 65: return "#f39c12"
    return "#e74c3c"


def render():
    _injetar_css()
    page_title("Histórico de Baterias", "Registro completo de todas as sessões lançadas")

    uid    = st.session_state.usuario["id"]
    df_all = ler_lancamentos(uid)
    df_e   = ler_erros(uid)

    if df_all.empty:
        st.info("Nenhum lançamento registrado ainda.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    meses_map = {
        "Todos": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
        "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
        "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
    }

    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 2, 2])

    with col_f1:
        st.caption("Mês")
        mes_sel = st.selectbox("Mês", list(meses_map.keys()), key="hist_mes",
                               label_visibility="collapsed")
    with col_f2:
        dts = pd.to_datetime(df_all["Data"], dayfirst=True, errors="coerce").dropna()
        anos_disp = ["Todos"] + sorted(dts.dt.year.unique().astype(str).tolist(), reverse=True)
        st.caption("Ano")
        ano_sel = st.selectbox("Ano", anos_disp, key="hist_ano",
                               label_visibility="collapsed")
    with col_f3:
        materias_disp = ["Todas"] + sorted(df_all["Materia"].dropna().unique().tolist())
        st.caption("Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="hist_mat",
                               label_visibility="collapsed")
    with col_f4:
        from config_fontes import get_label as _fonte_label
        fontes_slugs = sorted(df_all["Fonte"].dropna().unique().tolist())
        fontes_labels = ["Todas"] + [_fonte_label(s) for s in fontes_slugs]
        slug_map = {_fonte_label(s): s for s in fontes_slugs}
        st.caption("Fonte")
        fonte_label_sel = st.selectbox("Fonte", fontes_labels, key="hist_fonte",
                                       label_visibility="collapsed")
        fonte_sel = slug_map.get(fonte_label_sel, None)

    # Aplica filtros
    df = df_all.copy()
    df["_dt"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

    mes_int = meses_map.get(mes_sel)
    ano_int = int(ano_sel) if ano_sel != "Todos" else None
    if mes_int:
        df = df[df["_dt"].dt.month == mes_int]
    if ano_int:
        df = df[df["_dt"].dt.year == ano_int]
    if mat_sel != "Todas":
        df = df[df["Materia"] == mat_sel]
    if fonte_sel:
        df = df[df["Fonte"] == fonte_sel]

    df = df.drop(columns=["_dt"]).reset_index(drop=True)

    if df.empty:
        st.info("Nenhum lançamento encontrado para os filtros selecionados.")
        return

    # Coluna de status de erros
    ids_com_erros = set(df_e["ID Bateria"].dropna().unique()) if not df_e.empty else set()
    df["Com Erros"] = df["ID Bateria"].apply(lambda x: "Sim" if x in ids_com_erros else "Não")

    # ── Paginação ──────────────────────────────────────────────────────────────
    total = len(df)
    filtro_atual = (mes_sel, ano_sel, mat_sel, fonte_sel)
    if st.session_state.get("hist_filtro_ant") != filtro_atual:
        st.session_state.hist_page = 0
        st.session_state.hist_filtro_ant = filtro_atual
    if "hist_page" not in st.session_state:
        st.session_state.hist_page = 0

    total_pags = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(st.session_state.hist_page, total_pags - 1)
    df_page = df.iloc[page * PAGE_SIZE: page * PAGE_SIZE + PAGE_SIZE]

    st.caption(f"{total} registro(s) · Página {page + 1} de {total_pags}")

    # ── Tabela estilizada ──────────────────────────────────────────────────────
    th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
          "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(
        f'<th style="{th}">{c}</th>'
        for c in ["ID BATERIA", "MATÉRIA", "DATA", "ACERTOS", "TOTAL", "%", "FONTE", "ERROS"]
    )

    rows_html = ""
    for i, row in df_page.iterrows():
        perc = float(row["Percentual"]) if row["Percentual"] else 0.0
        cor  = _perc_color(perc)
        bg   = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        err_cor = "#e74c3c" if row["Com Erros"] == "Sim" else "#4ade80"
        td = "padding:10px 14px;vertical-align:middle;white-space:nowrap;"

        rows_html += f"""
        <tr style="background:{bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:700;color:#00b4a6;">{row['ID Bateria']}</td>
            <td style="{td}color:#fff;font-weight:600;">{row['Materia']}</td>
            <td style="{td}color:#8ab0c8;">{row['Data']}</td>
            <td style="{td}color:#c8d6e5;text-align:center;">{int(row['Acertos'])}</td>
            <td style="{td}color:#c8d6e5;text-align:center;">{int(row['Total'])}</td>
            <td style="{td}font-weight:800;color:{cor};text-align:center;">{perc:.1f}%</td>
            <td style="{td}color:#8ab0c8;font-size:0.82rem;">{row['Fonte'] or '—'}</td>
            <td style="{td}text-align:center;">
                <span style="color:{err_cor};font-weight:700;font-size:0.82rem;">{row['Com Erros']}</span>
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

    # ── Controles de paginação ────────────────────────────────────────────────
    col_ant, col_info, col_prox = st.columns([1, 3, 1])
    if col_ant.button("← Anterior", disabled=(page == 0), use_container_width=True):
        st.session_state.hist_page = page - 1
        st.rerun()
    if col_prox.button("Próximo →", disabled=(page >= total_pags - 1), use_container_width=True):
        st.session_state.hist_page = page + 1
        st.rerun()
