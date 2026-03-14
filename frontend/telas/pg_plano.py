"""
frontend/telas/pg_plano.py
Plano de estudos — dark mode compacto estilo SaaS.
Cards clicáveis com resumo gerado por IA ao expandir.
"""

import streamlit as st
from api_client import get_agenda, concluir_sessao, adiar_meta, gerar_resumo

# ── Constantes ────────────────────────────────────────────────────────────────

TIPO_LABEL = {
    "teoria_pdf":      "Teoria",
    "exercicios":      "Exercícios",
    "video":           "Vídeo",
    "flashcard_texto": "Flashcard",
    "calibracao":      "Calibração",
}
TIPO_COR = {
    "teoria_pdf":      "#3b82f6",
    "exercicios":      "#f59e0b",
    "video":           "#8b5cf6",
    "flashcard_texto": "#10b981",
    "calibracao":      "#00b4a6",
}

DARK_CSS = """
<style>
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

section[data-testid="stSidebar"] { background: #0d1b2a !important; }
section[data-testid="stSidebar"] * { color: #c8d6e5 !important; }

div[data-testid="stMetric"] {
    background: #1E2A36 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    border: 1px solid #1a3050 !important;
}
div[data-testid="stMetricValue"] { color: #E6EDF3 !important; }
div[data-testid="stMetricLabel"] { color: #7a9ab8 !important; font-size: 0.72rem !important; }

.stButton > button {
    background: #1E2A36 !important;
    color: #c8d6e5 !important;
    border: 1px solid #1a3050 !important;
    border-radius: 6px !important;
    font-size: 0.78rem !important;
    padding: 5px 10px !important;
    height: auto !important;
    transition: border-color 0.15s !important;
}
.stButton > button:hover { border-color: #00AFA0 !important; color: #E6EDF3 !important; }
.stButton > button[kind="primary"] {
    background: #00AFA0 !important;
    border-color: #00AFA0 !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover { background: #00c9b8 !important; }

.stSlider label, .stNumberInput label { color: #7a9ab8 !important; font-size: 0.75rem !important; }
.stDivider { border-color: #1a3050 !important; }
hr { border-color: #1a3050 !important; }
</style>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _prio(score: float) -> tuple:
    if score >= 0.7: return "Urgente", "#e74c3c"
    if score >= 0.5: return "Alta",    "#f59e0b"
    return "Normal", "#4ade80"


def _render_meta(sessoes: list, horas: float, dias: int):
    total_semana = max(1, int(horas * dias * 60 / 50))
    concluidas   = sum(1 for s in sessoes if st.session_state.get(f"ok_{s['sessao_id']}"))
    pct = min(int(concluidas / total_semana * 100), 100)
    cor = "#4ade80" if pct >= 70 else "#f59e0b" if pct >= 40 else "#e74c3c"
    st.html(
        f"<div style='background:#1E2A36;border-radius:10px;border:1px solid #1a3050;"
        f"padding:14px 18px;margin-bottom:14px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
        f"<span style='color:#E6EDF3;font-weight:700;font-size:0.88rem;'>Meta Semanal</span>"
        f"<span style='color:{cor};font-weight:800;font-size:0.95rem;'>"
        f"{concluidas}/{total_semana} tasks</span></div>"
        f"<div style='background:#0B1F2A;border-radius:6px;height:7px;'>"
        f"<div style='background:{cor};width:{pct}%;height:7px;border-radius:6px;'></div></div>"
        f"<div style='color:#7a9ab8;font-size:0.7rem;margin-top:5px;'>{pct}% concluído esta semana</div>"
        f"</div>"
    )


# ── Card ──────────────────────────────────────────────────────────────────────

def _card(s: dict, idx: int):
    tipo        = s.get("tipo", "")
    tipo_label  = TIPO_LABEL.get(tipo, tipo)
    tipo_cor    = TIPO_COR.get(tipo, "#7a9ab8")
    score       = s.get("score", 0)
    prio_label, prio_cor = _prio(score)
    dur         = s.get("duracao_planejada_min", 50)
    topico_nome = s.get("topico_nome", "Tópico")
    sid         = s.get("sessao_id", "")
    key         = f"t{idx}_{sid[:8]}"
    num         = idx + 1  # numeração da task

    # Hierarquia: matéria → tópico → subtópico
    materia     = s.get("materia", "") or s.get("area", "") or topico_nome
    topico_bloco = s.get("topico_bloco", "")
    subtopico   = s.get("subtopico", "") or topico_nome

    # Prompt para IA: usar o subtópico específico
    prompt_ia   = subtopico if subtopico else (topico_bloco if topico_bloco else materia)

    # ── Concluído: linha apagada ──────────────────────────────────────────────
    if st.session_state.get(f"ok_{sid}"):
        st.html(
            f"<div style='background:#1E2A36;border-radius:8px;padding:8px 14px;"
            f"margin-bottom:4px;border-left:3px solid #4ade80;opacity:0.45;'>"
            f"<span style='color:#4ade80;font-size:0.65rem;font-weight:700;'>✓ #{num} CONCLUÍDO</span>"
            f"<span style='color:#7a9ab8;margin-left:8px;font-size:0.8rem;'>"
            f"{materia}{' › ' + topico_bloco if topico_bloco else ''}"
            f"{' › ' + subtopico if subtopico and subtopico not in (materia, topico_bloco) else ''}"
            f"</span></div>"
        )
        return

    expandida = st.session_state.get(f"exp_{sid}", False)
    border    = "#00AFA0" if expandida else "#1a3050"
    bg_top    = "#243444"  if expandida else "#1E2A36"
    dot_cor   = "#f59e0b" if expandida else "#374151"  # amarelo=em andamento, cinza=pendente

    # Linha de hierarquia para exibição
    hierarquia_html = f"<span style='color:#E6EDF3;font-weight:700;font-size:0.9rem;'>{materia}</span>"
    if topico_bloco:
        hierarquia_html += f"<span style='color:#4a6a85;font-size:0.82rem;'> › {topico_bloco}</span>"
    if subtopico and subtopico not in (materia, topico_bloco):
        hierarquia_html += f"<span style='color:#c8d6e5;font-size:0.82rem;'> › {subtopico}</span>"

    # ── Cabeçalho do card ─────────────────────────────────────────────────────
    st.html(f"""
    <div style="background:{bg_top};border-radius:{'8px 8px 0 0' if expandida else '8px'};
        border:1px solid {border};border-bottom:{'none' if expandida else f'1px solid {border}'};
        padding:10px 14px;margin-bottom:0;cursor:pointer;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="color:#4a6a85;font-size:0.75rem;font-weight:700;flex-shrink:0;
                min-width:22px;text-align:right;">#{num}</span>
            <span style="color:{dot_cor};font-size:1rem;line-height:1;flex-shrink:0;">●</span>
            <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:baseline;gap:4px;flex-wrap:wrap;">
                    {hierarquia_html}
                </div>
                <div style="display:flex;gap:5px;margin-top:5px;align-items:center;flex-wrap:wrap;">
                    <span style="background:{tipo_cor}22;color:{tipo_cor};font-size:0.65rem;
                        font-weight:700;padding:2px 7px;border-radius:4px;">{tipo_label}</span>
                    <span style="color:#4a6a85;font-size:0.68rem;">{dur} min</span>
                    <span style="background:{prio_cor}22;color:{prio_cor};font-size:0.65rem;
                        font-weight:700;padding:2px 7px;border-radius:4px;">{prio_label}</span>
                </div>
            </div>
        </div>
    </div>
    """)

    # ── Botões de ação ────────────────────────────────────────────────────────
    col_exp, col_conc = st.columns([1, 1])
    with col_exp:
        lbl = "▲ Fechar" if expandida else "▼ Ver Resumo"
        if st.button(lbl, key=f"expbtn_{key}", use_container_width=True):
            st.session_state[f"exp_{sid}"] = not expandida
            st.rerun()
    with col_conc:
        if st.button("✓ Concluir", key=f"concbtn_{key}", use_container_width=True, type="primary"):
            st.session_state[f"fb_{sid}"] = True
            st.rerun()

    # ── Feedback rápido ───────────────────────────────────────────────────────
    if not expandida and st.session_state.get(f"fb_{sid}"):
        label_fb = subtopico[:40] if subtopico else materia[:40]
        st.html(f"""
        <div style="background:#0d1b2a;border:1px solid #00AFA0;border-radius:6px;
            padding:10px 14px;margin-top:2px;">
            <span style="color:#c8d6e5;font-size:0.8rem;">
                Como foi em <b>{label_fb}</b>?
            </span>
        </div>
        """)
        c1, c2 = st.columns(2)
        perc  = c1.slider("% acerto", 0, 100, 70, key=f"perc_{key}")
        dur_r = c2.number_input("Tempo (min)", 5, 120, dur, key=f"dur_{key}")
        b1, b2 = st.columns(2)
        if b1.button("Salvar", key=f"salvar_{key}", type="primary", use_container_width=True):
            res = concluir_sessao(sid, percentual=float(perc), duracao_real_min=int(dur_r))
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"fb_{sid}", None)
            if res and res.get("reforco_inserido"):
                st.session_state["_reforco_msg"] = (subtopico or materia)[:35]
            st.rerun()
        if b2.button("Pular", key=f"skip_{key}", use_container_width=True):
            concluir_sessao(sid, percentual=0, duracao_real_min=0)
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"fb_{sid}", None)
            st.rerun()

    # ── Painel expandido com resumo de IA ─────────────────────────────────────
    if expandida:
        cache_key = f"resumo_{sid}"
        if cache_key not in st.session_state:
            with st.spinner("Gerando resumo..."):
                resultado = gerar_resumo(prompt_ia)
            st.session_state[cache_key] = resultado or "Resumo não disponível para este tópico."

        resumo = st.session_state[cache_key]

        st.html(f"""
        <div style="background:#111e2b;border:1px solid #1a3050;border-top:none;
            border-radius:0 0 8px 8px;padding:14px 16px;margin-bottom:4px;">
            <div style="margin-bottom:12px;">
                <div style="color:#00b4a6;font-size:0.65rem;font-weight:700;
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">
                    Resumo da IA
                </div>
                <div style="background:#0B1F2A;border-radius:6px;padding:12px 14px;
                    border-left:3px solid #00AFA0;">
                    <p style="color:#c8d6e5;font-size:0.85rem;line-height:1.65;margin:0;">
                        {resumo}
                    </p>
                </div>
            </div>
        </div>
        """)

        c1, c2, c3 = st.columns([2, 2, 1])
        perc_e  = c1.slider("% acerto", 0, 100, 70, key=f"eperc_{key}")
        dur_e   = c2.number_input("Tempo (min)", 5, 120, dur, key=f"edur_{key}")
        if c3.button("✓", key=f"econc_{key}", type="primary", use_container_width=True):
            res = concluir_sessao(sid, percentual=float(perc_e), duracao_real_min=int(dur_e))
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"exp_{sid}", None)
            st.session_state.pop(cache_key, None)
            if res and res.get("reforco_inserido"):
                st.session_state["_reforco_msg"] = (subtopico or materia)[:35]
            st.rerun()

    st.html("<div style='height:4px'></div>")


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    usuario = st.session_state.get("usuario", {})
    horas   = float(usuario.get("horas_por_dia", 3.0))
    dias    = int(usuario.get("dias_semana", 5))
    data_p  = usuario.get("data_prova", "")
    area    = usuario.get("area_estudo", "")

    # Header
    st.html("""
    <div style="background:linear-gradient(135deg,#061020,#0d1b2a);border-radius:10px;
        padding:16px 24px;margin-bottom:16px;border-bottom:3px solid #00AFA0;
        box-shadow:0 4px 20px rgba(0,0,0,0.4);">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.3rem;">📋</span>
            <div>
                <div style="color:#E6EDF3;font-weight:800;font-size:1.15rem;
                    letter-spacing:0.1em;text-transform:uppercase;">
                    Plano de Estudos
                </div>
                <div style="color:#7a9ab8;font-size:0.75rem;margin-top:2px;">
                    Priorizado por urgência, lacuna e desempenho real
                </div>
            </div>
        </div>
    </div>
    """)

    msg_reforco = st.session_state.pop("_reforco_msg", None)
    if msg_reforco:
        st.warning(f"Reforço inserido: flashcard adicionado para '{msg_reforco}'.")

    # Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Carga/semana", f"{int(horas * dias)}h")
    c2.metric("Dias de estudo", f"{dias}")
    c3.metric("Max/sessão", "50 min")
    if data_p:
        st.markdown(
            f"<p style='color:#7a9ab8;font-size:0.8rem;margin-top:4px;'>"
            f"📅 Prova: <b style='color:#c8d6e5;'>{data_p}</b></p>",
            unsafe_allow_html=True,
        )

    # Guards
    if not st.session_state.get("onboarding_concluido") and not area:
        st.divider()
        st.info("Configure seu plano de estudos primeiro.")
        if st.button("Configurar →", type="primary"):
            st.session_state.ob_tela = 1
            st.session_state.pagina  = "onboarding"
            st.rerun()
        return

    if not st.session_state.get("api_token"):
        st.divider()
        st.warning("Sessão expirada. Faça logout e entre novamente.")
        if st.button("Sair", key="plano_logout"):
            st.session_state.clear()
            st.rerun()
        return

    # Carrega sessões
    sessoes_por_dia = max(1, int(horas * 60 / 50))
    total_buscar    = min(sessoes_por_dia * dias + 10, 50)

    with st.spinner("Calculando plano..."):
        sessoes = get_agenda(top=total_buscar)

    if not sessoes:
        st.divider()
        st.info("Nenhuma sessão pendente. Complete o onboarding para gerar seu plano.")
        if st.button("Ir para Onboarding →", type="primary"):
            st.session_state.ob_tela = 1
            st.session_state.pagina  = "onboarding"
            st.rerun()
        return

    st.divider()
    _render_meta(sessoes, horas, dias)

    col_adiar, col_dias, _ = st.columns([1, 1, 2])
    with col_dias:
        dias_adiar = st.selectbox(
            "Dias",
            options=[1, 2, 3],
            index=0,
            key="sel_dias_adiar",
            label_visibility="collapsed",
        )
    with col_adiar:
        if st.button(f"Adiar Meta (+{dias_adiar} dia{'s' if dias_adiar > 1 else ''})", key="btn_adiar", use_container_width=True):
            if adiar_meta(dias=dias_adiar):
                st.toast(f"Meta adiada em {dias_adiar} dia{'s' if dias_adiar > 1 else ''}.")
                for k in list(st.session_state.keys()):
                    if k.startswith(("ok_", "exp_", "resumo_")):
                        del st.session_state[k]
                st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Lista de tasks
    n_pend = sum(1 for s in sessoes if not st.session_state.get(f"ok_{s['sessao_id']}"))
    st.markdown(
        f"<div style='color:#7a9ab8;font-size:0.75rem;margin-bottom:8px;'>"
        f"<b style='color:#E6EDF3;'>{n_pend}</b> tasks pendentes</div>",
        unsafe_allow_html=True,
    )

    for idx, s in enumerate(sessoes):
        _card(s, idx)

    st.divider()
    if st.button("🔄 Recalcular plano", key="btn_recalc"):
        prefixes = ("ok_", "fb_", "exp_", "qr_", "qativo_", "perc_", "dur_", "resumo_", "eperc_", "edur_")
        for k in list(st.session_state.keys()):
            if any(k.startswith(p) for p in prefixes):
                del st.session_state[k]
        st.rerun()
