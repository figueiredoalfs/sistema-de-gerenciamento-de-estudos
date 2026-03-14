"""
pg_plano.py — Agenda do Dia
Tela principal: meta semanal, KPIs, tabela de atividades por prioridade.
"""
import streamlit as st
from database import get_perfil
from api_client import api_get_agenda, api_concluir_sessao, api_adiar_meta
from telas.components import page_header, kpi_card, score_to_stars, tipo_badge, tipo_label, _injetar_css


# ── Helpers ───────────────────────────────────────────────────────────────────

def _horas_str(minutos: int) -> str:
    h = minutos // 60
    m = minutos % 60
    if h and m:
        return f"{h}h {m}min"
    return f"{h}h" if h else f"{m}min"


def _render_meta_progress(sessoes: list, horas: float, dias: int):
    """Barra de progresso da meta semanal."""
    total_meta = max(1, int(horas * dias * 60 / 50))
    concluidas = sum(1 for s in sessoes if st.session_state.get(f"ok_{s['sessao_id']}"))
    pct = min(int(concluidas / total_meta * 100), 100)
    cor = "#27ae60" if pct >= 70 else "#f59e0b" if pct >= 40 else "#e74c3c"

    st.markdown(
        f'<div class="meta-card">'
        f'  <span class="meta-tag">Meta Semanal</span>'
        f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
        f'    <span style="color:#8ab0c8;font-size:0.8rem;">{concluidas} de {total_meta} sessões</span>'
        f'    <span style="color:{cor};font-weight:700;">{pct}%</span>'
        f'  </div>'
        f'  <div style="background:#0a1628;border-radius:6px;height:10px;">'
        f'    <div style="background:{cor};width:{pct}%;height:10px;border-radius:6px;transition:width 0.3s;"></div>'
        f'  </div>'
        f'  <div class="meta-info">{int(horas * dias)}h planejadas por semana · {dias} dias</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_proxima_sessao(sessoes: list):
    """Painel lateral com a próxima sessão pendente em destaque."""
    pendente = next(
        (s for s in sessoes if not st.session_state.get(f"ok_{s['sessao_id']}")),
        None,
    )
    if pendente:
        materia = pendente.get("materia") or pendente.get("area", "")
        dur = pendente.get("duracao_planejada_min", 50)
        st.markdown(
            f'<div class="prox-card">'
            f'  <div class="prox-titulo">Próxima Sessão</div>'
            f'  <div style="font-size:0.85rem;color:#e8f4ff;font-weight:600;margin-bottom:4px;">{materia}</div>'
            f'  <div style="font-size:0.75rem;color:#8ab0c8;">{tipo_label(pendente.get("tipo",""))} · {dur}min</div>'
            f'  <div class="prox-data">{score_to_stars(pendente.get("score", 0))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="prox-card">'
            '  <div class="prox-titulo">Meta</div>'
            '  <div class="prox-data">✅</div>'
            '  <div style="font-size:0.75rem;color:#8ab0c8;margin-top:6px;">Todas concluídas!</div>'
            '</div>',
            unsafe_allow_html=True,
        )


def _modal_concluir(s: dict, key_suffix: str):
    """Formulário inline para registrar conclusão de sessão."""
    sid = s["sessao_id"]
    dur = s.get("duracao_planejada_min", 50)

    with st.expander(f"✓ Concluir: {s.get('topico_nome','')[:40]}", expanded=True):
        c1, c2 = st.columns(2)
        perc  = c1.slider("% de acerto", 0, 100, 70, key=f"perc_{key_suffix}")
        dur_r = c2.number_input("Tempo real (min)", 5, 180, dur, key=f"dur_{key_suffix}")
        b1, b2 = st.columns(2)
        if b1.button("Salvar", key=f"salvar_{key_suffix}", type="primary"):
            res = api_concluir_sessao(sid, percentual=float(perc), duracao_real_min=int(dur_r))
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"modal_{sid}", None)
            if res and res.get("reforco_inserido"):
                st.session_state["_reforco_msg"] = s.get("topico_nome", "")[:35]
            st.rerun()
        if b2.button("Pular", key=f"skip_{key_suffix}"):
            api_concluir_sessao(sid, percentual=0, duracao_real_min=0)
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"modal_{sid}", None)
            st.rerun()


def _render_tabela(sessoes: list, prefix: str = "at"):
    """Tabela compacta de sessões com colunas: #, Matéria, Tipo, Tópico, Relevância, Duração, Desempenho, Ação."""
    if not sessoes:
        st.info("Nenhuma sessão pendente. Complete o onboarding para gerar seu plano.")
        return

    # Cabeçalho
    cols = st.columns([0.4, 1.8, 1.2, 2.8, 1.3, 0.8, 0.9, 1.1])
    for label, col in zip(
        ["#", "Matéria", "Tipo", "Tópico", "Relevância", "Duração", "Desempenho", ""],
        cols,
    ):
        col.markdown(f"<small><b>{label}</b></small>", unsafe_allow_html=True)

    st.markdown('<hr style="margin:4px 0 8px 0;border-color:#1e3040;">', unsafe_allow_html=True)

    for i, s in enumerate(sessoes, 1):
        sid     = s["sessao_id"]
        concluida = st.session_state.get(f"ok_{sid}", False)
        materia = s.get("materia") or s.get("area", "—")
        topico  = s.get("topico_nome", "—")
        tipo    = s.get("tipo", "")
        dur     = s.get("duracao_planejada_min", 50)
        score   = s.get("score", 0)
        desemp  = s.get("desempenho")
        desemp_txt = f"{desemp:.0f}%" if desemp is not None else "—"
        estrelas = score_to_stars(score)

        opacity = "0.45" if concluida else "1"
        row_bg  = "#122033" if concluida else ("transparent" if i % 2 == 0 else "#0e1d2b")

        cols = st.columns([0.4, 1.8, 1.2, 2.8, 1.3, 0.8, 0.9, 1.1])
        style = f"opacity:{opacity};"

        cols[0].markdown(f"<span style='{style}color:#8ab0c8;'>{i}</span>", unsafe_allow_html=True)
        cols[1].markdown(f"<span style='{style}color:#e8f4ff;font-weight:600;'>{materia[:22]}</span>", unsafe_allow_html=True)
        cols[2].markdown(tipo_badge(tipo) if not concluida else f"<span style='color:#8ab0c8;font-size:0.75rem;'>{tipo_label(tipo)}</span>", unsafe_allow_html=True)
        cols[3].markdown(f"<span style='{style}color:#c8d6e5;'>{topico[:38]}</span>", unsafe_allow_html=True)
        cols[4].markdown(f"<span style='{style}color:#f0c040;'>{estrelas}</span>", unsafe_allow_html=True)
        cols[5].markdown(f"<span style='{style}color:#8ab0c8;'>{dur}min</span>", unsafe_allow_html=True)
        cols[6].markdown(f"<span style='{style}color:#8ab0c8;'>{desemp_txt}</span>", unsafe_allow_html=True)

        if concluida:
            cols[7].markdown("<span style='color:#27ae60;font-size:0.8rem;'>✓ Feito</span>", unsafe_allow_html=True)
        else:
            if cols[7].button("✓", key=f"{prefix}_btn_{sid}", help="Concluir sessão"):
                st.session_state[f"modal_{sid}"] = True
                st.rerun()

        # Modal inline abaixo da linha
        if st.session_state.get(f"modal_{sid}"):
            _modal_concluir(s, key_suffix=f"{prefix}_{sid[:8]}")


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    _injetar_css()

    usuario_id = st.session_state.usuario["id"]
    perfil = get_perfil(usuario_id)
    horas  = float(perfil.get("horas_dia") or 3.0)
    dias   = int(perfil.get("dias_semana") or 5)

    # Verificações de estado
    if not perfil.get("plano") == "ativo":
        page_header("Agenda do Dia", "Configure seu plano para começar")
        st.info("Você ainda não configurou seu plano de estudos.")
        if st.button("Configurar agora →", type="primary"):
            st.session_state.ob_tela = 1
            st.session_state.pagina  = "onboarding"
            st.rerun()
        return

    if not st.session_state.get("api_token"):
        page_header("Agenda do Dia", "")
        st.warning("Sessão expirada. Saia e entre novamente para continuar.")
        if st.button("Sair", key="plano_logout"):
            st.session_state.clear()
            st.rerun()
        return

    # Header
    page_header("Agenda do Dia", "Acompanhe seu progresso e veja o que falta para atingir sua meta")

    # Busca sessões da API
    sessoes_por_dia = max(1, int(horas * 60 / 50))
    total_buscar    = min(sessoes_por_dia * dias + 10, 50)
    with st.spinner("Calculando prioridades..."):
        sessoes = api_get_agenda(top=total_buscar)

    # Meta + próxima sessão
    col_meta, col_prox = st.columns([3, 1])
    with col_meta:
        _render_meta_progress(sessoes, horas, dias)
    with col_prox:
        _render_proxima_sessao(sessoes)

    # Notificação de reforço inserido
    msg_reforco = st.session_state.pop("_reforco_msg", None)
    if msg_reforco:
        st.warning(f"Reforço inserido: Flashcard adicionado para '{msg_reforco}' (desempenho < 60%).")

    # KPIs
    total_sessoes   = len(sessoes)
    concluidas_hoje = sum(1 for s in sessoes if st.session_state.get(f"ok_{s['sessao_id']}"))
    scores          = [s.get("score", 0) for s in sessoes if s.get("score")]
    desemp_medio    = sum(scores) / len(scores) * 100 if scores else 0
    carga_plan_min  = sum(s.get("duracao_planejada_min", 50) for s in sessoes if not st.session_state.get(f"ok_{s['sessao_id']}"))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Sessões pendentes", str(total_sessoes - concluidas_hoje), "📋", "#3a86ff")
    with c2:
        kpi_card("Concluídas hoje", str(concluidas_hoje), "✅", "#06d6a0")
    with c3:
        kpi_card("Prioridade média", f"{desemp_medio:.0f}%", "🎯", "#f77f00")
    with c4:
        kpi_card("Carga pendente", _horas_str(carga_plan_min), "⏱", "#9b5de5")

    st.markdown("<br>", unsafe_allow_html=True)

    # Separar atividades normais de reforços (flashcard gerado automaticamente)
    reforcos   = [s for s in sessoes if s.get("tipo") == "flashcard_texto" and s.get("score", 1) < 0.3]
    atividades = [s for s in sessoes if s not in reforcos]

    # Abas
    tab_ativ, tab_ref, tab_adiar = st.tabs([
        f"Atividades | {len(atividades)}",
        f"Reforços | {len(reforcos)}",
        "⚙️ Opções",
    ])

    with tab_ativ:
        _render_tabela(atividades, prefix="at")

    with tab_ref:
        if reforcos:
            _render_tabela(reforcos, prefix="rf")
        else:
            st.info("Nenhum reforço pendente. Os reforços aparecem quando você tem desempenho < 60% em uma sessão.")

    with tab_adiar:
        st.markdown("##### Adiar todas as sessões")
        st.caption("Use com moderação — adia as sessões pendentes em N dias.")
        dias_adiar = st.selectbox("Adiar em", [1, 3, 7], index=0, key="dias_adiar_sel")
        if st.button(f"Adiar em {dias_adiar} dia(s)", key="btn_adiar"):
            if api_adiar_meta(dias=dias_adiar):
                st.toast(f"Sessões adiadas em {dias_adiar} dia(s).")
                for k in list(st.session_state.keys()):
                    if k.startswith("ok_") or k.startswith("exp_") or k.startswith("modal_"):
                        del st.session_state[k]
                st.rerun()

        st.markdown("---")
        st.markdown("##### Recalcular plano")
        if st.button("Recalcular", key="btn_recalc"):
            prefixes = ("ok_", "fb_", "exp_", "modal_", "qr_", "qativo_", "perc_", "dur_")
            for k in list(st.session_state.keys()):
                if any(k.startswith(p) for p in prefixes):
                    del st.session_state[k]
            st.rerun()
