"""
pg_erros_criticos.py
Gestão de erros: filtros por matéria/status, badges e botão de resolução.
"""

import pandas as pd
import streamlit as st

from api_client import api_atualizar_status_erro, api_listar_erros
from telas.components import _injetar_css, page_title

STATUS_LABEL = {
    "pendente":   ("Pendente",   "#f39c12"),
    "em_revisao": ("Em revisão", "#3a86ff"),
    "resolvido":  ("Resolvido",  "#4ade80"),
}


def _header():
    _injetar_css()
    page_title("Erros Pendentes", "Questões com erro que precisam de revisão")


def _badge(texto: str, cor: str) -> str:
    return (
        f'<span style="background:{cor}22;color:{cor};border:1px solid {cor}55;'
        f'border-radius:4px;padding:2px 8px;font-size:0.72rem;font-weight:700;'
        f'white-space:nowrap;">{texto}</span>'
    )


def render():
    _header()

    erros = api_listar_erros()

    if not erros:
        st.info("Nenhum erro registrado ainda.")
        return

    df = pd.DataFrame(erros)
    # Normaliza colunas para os nomes usados na tela
    df = df.rename(columns={
        "id": "ID",
        "materia": "Materia",
        "topico_texto": "Topico",
        "qtd_erros": "Qtd Erros",
        "data": "Data",
        "status": "Status",
        "id_bateria": "ID Bateria",
    })
    df["Topico"]   = df["Topico"].fillna("—")
    df["Status"]   = df["Status"].fillna("pendente")
    df["Data"]     = pd.to_datetime(df["Data"], errors="coerce").dt.strftime("%d/%m/%Y")

    # ── Filtros ───────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns([2, 2])

    materias_disp = ["Todas"] + sorted(df["Materia"].dropna().unique().tolist())
    with col_f1:
        st.caption("Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="ec_mat",
                               label_visibility="collapsed")

    with col_f2:
        st.caption("Status")
        status_sel = st.selectbox("Status", ["Pendentes", "Em Revisão", "Resolvidos", "Todos"],
                                  key="ec_status", label_visibility="collapsed")

    # Aplica filtros
    df_f = df.copy()
    if mat_sel != "Todas":
        df_f = df_f[df_f["Materia"] == mat_sel]
    status_map = {"Pendentes": "pendente", "Em Revisão": "em_revisao", "Resolvidos": "resolvido"}
    if status_sel in status_map:
        df_f = df_f[df_f["Status"] == status_map[status_sel]]

    df_f = df_f.sort_values(["Status", "Data"], ascending=[True, False]).reset_index(drop=True)

    # ── Métricas ──────────────────────────────────────────────────────────────
    n_pend = int((df["Status"] == "pendente").sum())
    n_rev  = int((df["Status"] == "resolvido").sum())
    n_tot  = len(df)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total de Erros",  n_tot)
    k2.metric("Pendentes",       n_pend)
    k3.metric("Resolvidos",      n_rev)

    if df_f.empty:
        st.info("Nenhum erro encontrado para os filtros selecionados.")
        return

    st.markdown(f"**{len(df_f)}** registro(s)")

    # ── Tabela de erros ───────────────────────────────────────────────────────
    th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
          "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(
        f'<th style="{th}">{c}</th>'
        for c in ["MATÉRIA", "TÓPICO", "QTD", "DATA", "STATUS", "AÇÃO"]
    )

    rows_html = ""
    for i, row in df_f.iterrows():
        st_txt, st_cor = STATUS_LABEL.get(row["Status"], ("—", "#8ab0c8"))
        row_bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        td = "padding:10px 14px;vertical-align:middle;"

        rows_html += f"""
        <tr style="background:{row_bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:700;color:#fff;">{row['Materia']}</td>
            <td style="{td}color:#c8d6e5;">{row['Topico']}</td>
            <td style="{td}color:#8ab0c8;text-align:center;">{row['Qtd Erros']}</td>
            <td style="{td}color:#8ab0c8;font-size:0.85rem;">{row['Data'] or '—'}</td>
            <td style="{td}">{_badge(st_txt, st_cor)}</td>
            <td style="{td}">BOTAO_{row['ID']}</td>
        </tr>"""

    st.html(f"""
        <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
            padding:10px 18px;border-bottom:2px solid #e74c3c;">
            <span style="color:#fff;font-weight:700;font-size:0.82rem;
                letter-spacing:0.12em;text-transform:uppercase;">Lista de Erros</span>
        </div>
        <div style="background:#0d1b2a;border-radius:0 0 8px 8px;overflow:hidden;
            border:1px solid #1a3050;border-top:none;box-shadow:0 6px 20px rgba(0,0,0,0.4);
            margin-bottom:16px;">
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:#061020;">{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """)

    # ── Botões de alteração de status (fora do HTML) ──────────────────────────
    st.markdown("**Alterar status dos erros:**")
    for _, row in df_f.iterrows():
        eid    = row["ID"]
        status = row["Status"]
        topico = row["Topico"]
        mat    = row["Materia"]

        col_lbl, col_btn1, col_btn2 = st.columns([4, 1, 1])
        col_lbl.markdown(
            f'<span style="color:#c8d6e5;font-size:0.85rem;">'
            f'<b>{mat}</b> — {topico}</span>',
            unsafe_allow_html=True,
        )
        if status == "pendente":
            if col_btn1.button("📝 Em revisão", key=f"rev_{eid}", use_container_width=True):
                api_atualizar_status_erro(eid, "em_revisao")
                st.rerun()
            if col_btn2.button("✓ Resolvido", key=f"res_{eid}", use_container_width=True):
                api_atualizar_status_erro(eid, "resolvido")
                st.rerun()
        elif status == "em_revisao":
            if col_btn1.button("✓ Resolvido", key=f"res_{eid}", use_container_width=True):
                api_atualizar_status_erro(eid, "resolvido")
                st.rerun()
            if col_btn2.button("↩ Pendente", key=f"pend_{eid}", use_container_width=True):
                api_atualizar_status_erro(eid, "pendente")
                st.rerun()
        else:
            if col_btn1.button("↩ Pendente", key=f"pend_{eid}", use_container_width=True):
                api_atualizar_status_erro(eid, "pendente")
                st.rerun()
