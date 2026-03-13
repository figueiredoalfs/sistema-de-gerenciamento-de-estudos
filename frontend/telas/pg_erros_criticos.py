"""
frontend/telas/pg_erros_criticos.py
Gestão de erros críticos: filtros, badges e atualização de status.
Dados exclusivamente via API (sem database.py).
"""

import streamlit as st
from api_client import listar_erros, atualizar_status_erro

# Tipo vem do campo 'observacao' (gravado como slug pelo pg_lancar_bateria)
TIPO_LABEL = {
    "nao_sabia": ("Não sabia", "#e74c3c"),
    "confundiu": ("Confundi",  "#f39c12"),
    "esqueceu":  ("Esqueci",   "#8ab0c8"),
}

STATUS_LABEL = {
    "pendente":   ("Pendente",   "#f39c12"),
    "em_revisao": ("Em Revisão", "#8b5cf6"),
    "resolvido":  ("Resolvido",  "#4ade80"),
}


def _badge(texto: str, cor: str) -> str:
    return (
        f'<span style="background:{cor}22;color:{cor};border:1px solid {cor}55;'
        f'border-radius:4px;padding:2px 8px;font-size:0.72rem;font-weight:700;">{texto}</span>'
    )


def render():
    st.html("""
        <div style="background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;
            text-align:center;border-bottom:3px solid #e74c3c;
            box-shadow:0 4px 16px rgba(0,0,0,0.35);">
            <span style="font-size:1.4rem;">&#128680;</span>
            <span style="color:#fff;font-weight:800;font-size:1.3rem;
                letter-spacing:0.12em;margin-left:10px;text-transform:uppercase;">
                Erros Críticos
            </span>
        </div>
    """)

    with st.spinner("Carregando erros..."):
        todos_erros = listar_erros()

    if not todos_erros:
        st.info("Nenhum erro registrado ainda.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    materias_disp = ["Todas"] + sorted({e.get("materia", "") for e in todos_erros if e.get("materia")})

    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        st.caption("Matéria")
        mat_sel = st.selectbox("Matéria", materias_disp, key="ec_mat", label_visibility="collapsed")
    with col_f2:
        st.caption("Status")
        status_sel = st.selectbox("Status", ["Pendentes", "Em Revisão", "Resolvidos", "Todos"],
                                  key="ec_status", label_visibility="collapsed")
    with col_f3:
        st.caption("Tipo do Erro")
        tipo_opts = ["Todos", "Não sabia", "Confundi", "Esqueci"]
        tipo_sel  = st.selectbox("Tipo", tipo_opts, key="ec_tipo", label_visibility="collapsed")

    # Aplica filtros
    df_f = todos_erros
    if mat_sel != "Todas":
        df_f = [e for e in df_f if e.get("materia") == mat_sel]

    status_map = {"Pendentes": "pendente", "Em Revisão": "em_revisao", "Resolvidos": "resolvido"}
    if status_sel in status_map:
        df_f = [e for e in df_f if e.get("status") == status_map[status_sel]]

    tipo_inv = {"Não sabia": "nao_sabia", "Confundi": "confundiu", "Esqueci": "esqueceu"}
    if tipo_sel != "Todos":
        slug = tipo_inv[tipo_sel]
        df_f = [e for e in df_f if e.get("observacao") == slug]

    # ── Métricas ──────────────────────────────────────────────────────────────
    n_pend  = sum(1 for e in todos_erros if e.get("status") == "pendente")
    n_rev   = sum(1 for e in todos_erros if e.get("status") == "em_revisao")
    n_resol = sum(1 for e in todos_erros if e.get("status") == "resolvido")
    n_tot   = len(todos_erros)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total",      n_tot)
    k2.metric("Pendentes",  n_pend)
    k3.metric("Em Revisão", n_rev)
    k4.metric("Resolvidos", n_resol)

    if not df_f:
        st.info("Nenhum erro encontrado para os filtros selecionados.")
        return

    st.markdown(f"**{len(df_f)}** registro(s)")

    # ── Tabela de erros ───────────────────────────────────────────────────────
    th = ("padding:10px 14px;text-align:left;font-size:0.72rem;"
          "letter-spacing:0.08em;color:#7a9ab8;font-weight:600;white-space:nowrap;")
    header_html = "".join(
        f'<th style="{th}">{c}</th>'
        for c in ["MATÉRIA", "TÓPICO", "TIPO", "DATA", "STATUS"]
    )

    rows_html = ""
    for i, e in enumerate(df_f):
        obs       = e.get("observacao", "")
        tipo_txt, tipo_cor = TIPO_LABEL.get(obs, ("—", "#8ab0c8"))
        st_txt,   st_cor   = STATUS_LABEL.get(e.get("status", ""), ("—", "#8ab0c8"))
        data_str  = str(e.get("data", "—"))[:10]
        row_bg    = "#0a1628" if i % 2 == 0 else "#0d1b2a"
        td        = "padding:10px 14px;vertical-align:middle;"

        rows_html += f"""
        <tr style="background:{row_bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:700;color:#fff;">{e.get('materia','—')}</td>
            <td style="{td}color:#c8d6e5;">{e.get('topico_texto','—')}</td>
            <td style="{td}">{_badge(tipo_txt, tipo_cor)}</td>
            <td style="{td}color:#8ab0c8;font-size:0.85rem;">{data_str}</td>
            <td style="{td}">{_badge(st_txt, st_cor)}</td>
        </tr>"""

    st.html(f"""
        <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
            padding:10px 18px;border-bottom:2px solid #e74c3c;">
            <span style="color:#fff;font-weight:700;font-size:0.82rem;
                letter-spacing:0.12em;text-transform:uppercase;">Lista de Erros</span>
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

    # ── Botões de alteração de status ─────────────────────────────────────────
    st.markdown("**Alterar status:**")
    for e in df_f:
        eid    = e.get("id", "")
        status = e.get("status", "pendente")
        topico = e.get("topico_texto", "—")
        mat    = e.get("materia", "—")

        col_lbl, col_btn1, col_btn2 = st.columns([4, 1, 1])
        col_lbl.markdown(
            f'<span style="color:#c8d6e5;font-size:0.85rem;"><b>{mat}</b> — {topico}</span>',
            unsafe_allow_html=True,
        )
        if status == "pendente":
            if col_btn1.button("Em Revisão", key=f"rev_{eid}", use_container_width=True):
                atualizar_status_erro(eid, "em_revisao")
                st.rerun()
        if status in ("pendente", "em_revisao"):
            if col_btn2.button("Resolvido", key=f"resol_{eid}", use_container_width=True, type="primary"):
                atualizar_status_erro(eid, "resolvido")
                st.rerun()
        if status in ("em_revisao", "resolvido"):
            if col_btn1.button("↩ Pendente", key=f"pend_{eid}", use_container_width=True):
                atualizar_status_erro(eid, "pendente")
                st.rerun()
