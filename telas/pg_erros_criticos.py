"""
pg_erros_criticos.py
Gestão de erros: filtros por matéria/status, badges de tipo e botão de resolução.
"""

import streamlit as st
from database import ler_erros, atualizar_status_erro
from telas.components import page_title, _injetar_css

TIPO_LABEL = {
    "nao_sabia":  ("Não sabia",  "#e74c3c"),
    "confundiu":  ("Confundi",   "#f39c12"),
    "esqueceu":   ("Esqueci",    "#8ab0c8"),
}

STATUS_LABEL = {
    "pendente":  ("Pendente",  "#f39c12"),
    "revisado":  ("Revisado",  "#4ade80"),
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

    uid = st.session_state.usuario["id"]
    df  = ler_erros(uid)

    if df.empty:
        st.info("Nenhum erro registrado ainda.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])

    materias_disp = ["Todas"] + sorted(df["Materia"].dropna().unique().tolist())
    with col_f1:
        st.caption("Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="ec_mat",
                               label_visibility="collapsed")

    with col_f2:
        st.caption("Status")
        status_sel = st.selectbox("Status", ["Pendentes", "Revisados", "Todos"],
                                  key="ec_status", label_visibility="collapsed")

    with col_f3:
        st.caption("Tipo do Erro")
        tipo_opts = ["Todos", "Não sabia", "Confundi", "Esqueci"]
        tipo_sel  = st.selectbox("Tipo", tipo_opts, key="ec_tipo",
                                 label_visibility="collapsed")

    # Aplica filtros
    df_f = df.copy()
    if mat_sel != "Todas":
        df_f = df_f[df_f["Materia"] == mat_sel]
    if status_sel == "Pendentes":
        df_f = df_f[df_f["Status"] == "pendente"]
    elif status_sel == "Revisados":
        df_f = df_f[df_f["Status"] == "revisado"]

    tipo_map_inv = {"Não sabia": "nao_sabia", "Confundi": "confundiu", "Esqueci": "esqueceu"}
    if tipo_sel != "Todos":
        df_f = df_f[df_f["Tipo Erro"] == tipo_map_inv[tipo_sel]]

    df_f = df_f.sort_values(["Status", "Data"], ascending=[True, False]).reset_index(drop=True)

    # ── Métricas ──────────────────────────────────────────────────────────────
    n_pend = int((df["Status"] == "pendente").sum())
    n_rev  = int((df["Status"] == "revisado").sum())
    n_tot  = len(df)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total de Erros",  n_tot)
    k2.metric("Pendentes",       n_pend)
    k3.metric("Revisados",       n_rev)

    if df_f.empty:
        st.info("Nenhum erro encontrado para os filtros selecionados.")
        return

    st.markdown(f"**{len(df_f)}** registro(s)")

    # ── Tabela de erros ───────────────────────────────────────────────────────
    th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
          "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(
        f'<th style="{th}">{c}</th>'
        for c in ["MATÉRIA", "TÓPICO", "TIPO", "DATA", "STATUS", "AÇÃO"]
    )

    rows_html = ""
    for i, row in df_f.iterrows():
        tipo_txt, tipo_cor = TIPO_LABEL.get(row["Tipo Erro"], ("—", "#8ab0c8"))
        st_txt,   st_cor   = STATUS_LABEL.get(row["Status"],   ("—", "#8ab0c8"))
        row_bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        td = "padding:10px 14px;vertical-align:middle;"

        rows_html += f"""
        <tr style="background:{row_bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:700;color:#fff;">{row['Materia']}</td>
            <td style="{td}color:#c8d6e5;">{row['Topico']}</td>
            <td style="{td}">{_badge(tipo_txt, tipo_cor)}</td>
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
        eid    = int(row["ID"])
        status = row["Status"]
        topico = row["Topico"]
        mat    = row["Materia"]

        col_lbl, col_btn = st.columns([4, 1])
        col_lbl.markdown(
            f'<span style="color:#c8d6e5;font-size:0.85rem;">'
            f'<b>{mat}</b> — {topico}</span>',
            unsafe_allow_html=True,
        )
        if status == "pendente":
            if col_btn.button("✓ Revisado", key=f"rev_{eid}", use_container_width=True):
                atualizar_status_erro(eid, "revisado", uid)
                st.rerun()
        else:
            if col_btn.button("↩ Pendente", key=f"pend_{eid}", use_container_width=True):
                atualizar_status_erro(eid, "pendente", uid)
                st.rerun()
