"""
frontend/telas/pg_plano.py
Plano semanal com lista de tasks, meta semanal e quiz inline.
Dados exclusivamente via API (sem database.py).
"""

import streamlit as st
from api_client import get_agenda, concluir_sessao, adiar_meta

TIPO_LABEL = {
    "teoria_pdf":      "Teoria",
    "exercicios":      "Exercicios",
    "video":           "Video",
    "flashcard_texto": "Flashcard",
    "calibracao":      "Calibracao",
}
TIPO_COR = {
    "teoria_pdf":      "#3b82f6",
    "exercicios":      "#f59e0b",
    "video":           "#8b5cf6",
    "flashcard_texto": "#10b981",
    "calibracao":      "#00b4a6",
}
QUIZ_TEMPLATES = {
    "teoria_pdf":      ["Qual o conceito central deste tópico?", "Cite um exemplo prático.", "Qual a principal regra ou princípio?"],
    "exercicios":      ["Qual foi o maior erro neste tópico?", "Qual questão achou mais difícil?", "O que precisa revisar?"],
    "flashcard_texto": ["Explique com suas palavras o conceito.", "Qual a diferença entre os termos?", "Quando este conceito se aplica?"],
    "video":           ["O que você aprendeu no vídeo?", "Qual ponto foi mais relevante?", "O que faz sentido com o que já sabia?"],
}


def _prio(score):
    if score >= 0.7:
        return "URGENTE", "#e74c3c"
    elif score >= 0.5:
        return "Alta", "#f59e0b"
    return "Normal", "#27ae60"


def _render_meta(sessoes, horas, dias):
    total_semana = max(1, int(horas * dias * 60 / 50))
    concluidas   = sum(1 for s in sessoes if st.session_state.get(f"ok_{s['sessao_id']}"))
    pct = min(int(concluidas / total_semana * 100), 100)
    cor = "#27ae60" if pct >= 70 else "#f59e0b" if pct >= 40 else "#e74c3c"
    st.html(
        f"<div style='background:#0d1b2a;border-radius:10px;border:1px solid #1a3050;"
        f"padding:14px 18px;margin-bottom:12px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
        f"<span style='color:#ffffff;font-weight:700;font-size:0.9rem;'>Meta Semanal</span>"
        f"<span style='color:{cor};font-weight:800;font-size:1rem;'>{concluidas}/{total_semana} tasks</span></div>"
        f"<div style='background:#0a1628;border-radius:6px;height:10px;'>"
        f"<div style='background:{cor};width:{pct}%;height:10px;border-radius:6px;'></div></div>"
        f"<div style='color:#7a9ab8;font-size:0.72rem;margin-top:6px;'>{pct}% concluído esta semana</div></div>"
    )


def _quiz(topico, tipo, key):
    perguntas = QUIZ_TEMPLATES.get(tipo, QUIZ_TEMPLATES["teoria_pdf"])
    st.markdown(
        f"<div style='background:#061020;border-radius:8px;border:1px solid #00b4a6;"
        f"padding:12px 16px;margin-top:8px;'>"
        f"<span style='color:#00b4a6;font-weight:700;font-size:0.82rem;'>"
        f"Questionário: {topico[:40]}</span></div>",
        unsafe_allow_html=True,
    )
    respostas = []
    for i, pergunta in enumerate(perguntas):
        r = st.text_area(pergunta, key=f"qr_{key}_{i}", height=60, placeholder="Sua resposta...")
        respostas.append(r.strip())
    respondidas = sum(1 for r in respostas if len(r) > 5)
    if respondidas < 2:
        st.caption(f"Responda pelo menos 2 perguntas para concluir ({respondidas}/2)")
    return respondidas >= 2


def _card(s, idx):
    tipo       = s.get("tipo", "")
    tipo_label = TIPO_LABEL.get(tipo, tipo)
    tipo_cor   = TIPO_COR.get(tipo, "#7a9ab8")
    score      = s.get("score", 0)
    prio_label, prio_cor = _prio(score)
    dur    = s.get("duracao_planejada_min", 50)
    topico = s.get("topico_nome", "Tópico")
    area   = s.get("area", "")
    sid    = s.get("sessao_id", "")
    key    = f"t{idx}_{sid[:8]}"

    if st.session_state.get(f"ok_{sid}"):
        st.html(
            f"<div style='background:#0a1628;border-radius:8px;border-left:4px solid #27ae60;"
            f"padding:8px 16px;margin-bottom:4px;opacity:0.5;'>"
            f"<span style='color:#27ae60;font-size:0.75rem;'>Concluído</span>"
            f"<span style='color:#7a9ab8;margin-left:8px;font-size:0.82rem;'>{topico[:50]}</span></div>"
        )
        return

    expandido = st.session_state.get(f"exp_{sid}", False)
    col_card, col_btn = st.columns([5, 1])

    with col_card:
        seta = "v" if expandido else ">"
        if st.button(
            f"[{seta}] [{tipo_label}]  {topico[:45]}  |  {dur}min  |  {prio_label}",
            key=f"card_{key}",
            use_container_width=True,
        ):
            st.session_state[f"exp_{sid}"] = not expandido
            st.rerun()

    with col_btn:
        if not expandido:
            if st.button("Concluir", key=f"rapido_{key}", type="primary", use_container_width=True):
                st.session_state[f"fb_{sid}"] = True
                st.rerun()

    # Feedback rápido
    if not expandido and st.session_state.get(f"fb_{sid}"):
        st.markdown(
            f"<div style='background:#0d1b2a;border:1px solid #00b4a6;border-radius:8px;"
            f"padding:10px 16px;margin-bottom:4px;'>"
            f"<span style='color:#c8d6e5;font-size:0.82rem;'>Como foi em <b>{topico[:35]}</b>?</span></div>",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        perc  = c1.slider("% acerto", 0, 100, 70, key=f"perc_{key}")
        dur_r = c2.number_input("Tempo (min)", 5, 120, dur, key=f"dur_{key}")
        b1, b2 = st.columns(2)
        if b1.button("Salvar", key=f"salvar_{key}", type="primary"):
            res = concluir_sessao(sid, percentual=float(perc), duracao_real_min=int(dur_r))
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"fb_{sid}", None)
            if res and res.get("reforco_inserido"):
                st.session_state["_reforco_msg"] = topico[:35]
            st.rerun()
        if b2.button("Pular", key=f"skip_{key}"):
            concluir_sessao(sid, percentual=0, duracao_real_min=0)
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"fb_{sid}", None)
            st.rerun()

    # Painel expandido
    if expandido:
        st.html(
            f"<div style='background:linear-gradient(135deg,#0a1628,#0d1b2a);"
            f"border-radius:0 0 8px 8px;border:1px solid #1a3050;border-top:none;"
            f"padding:14px 16px;margin-bottom:4px;'>"
            f"<div style='display:flex;gap:8px;margin-bottom:8px;'>"
            f"<span style='background:{tipo_cor}22;color:{tipo_cor};font-size:0.7rem;"
            f"font-weight:700;padding:3px 10px;border-radius:4px;'>{tipo_label}</span>"
            f"<span style='background:{prio_cor}22;color:{prio_cor};font-size:0.68rem;"
            f"padding:3px 8px;border-radius:4px;font-weight:700;'>{prio_label}</span>"
            f"<span style='color:#7a9ab8;font-size:0.7rem;margin-left:auto;'>{dur} min</span></div>"
            f"<div style='color:#ffffff;font-weight:700;'>{topico}</div>"
            f"<div style='color:#7a9ab8;font-size:0.78rem;margin-top:2px;'>{area}</div></div>"
        )

        c_quiz, c_fechar = st.columns(2)
        with c_quiz:
            quiz_ativo = st.session_state.get(f"qativo_{sid}", False)
            lbl = "Fechar Questionário" if quiz_ativo else "Realizar Questionário"
            if st.button(lbl, key=f"qbtn_{key}", use_container_width=True):
                st.session_state[f"qativo_{sid}"] = not quiz_ativo
                st.rerun()
        with c_fechar:
            if st.button("Fechar", key=f"fechar_{key}", use_container_width=True):
                st.session_state[f"exp_{sid}"] = False
                st.rerun()

        if st.session_state.get(f"qativo_{sid}"):
            quiz_ok = _quiz(topico, tipo, key)
            if quiz_ok:
                c1, c2 = st.columns(2)
                perc  = c1.slider("% acerto", 0, 100, 70, key=f"qperc_{key}")
                dur_r = c2.number_input("Tempo (min)", 5, 120, dur, key=f"qdur_{key}")
                if st.button("Concluir Task", key=f"qconcluir_{key}", type="primary", use_container_width=True):
                    res = concluir_sessao(sid, percentual=float(perc), duracao_real_min=int(dur_r))
                    st.session_state[f"ok_{sid}"] = True
                    st.session_state.pop(f"qativo_{sid}", None)
                    st.session_state.pop(f"exp_{sid}", None)
                    if res and res.get("reforco_inserido"):
                        st.session_state["_reforco_msg"] = topico[:35]
                    st.rerun()


def render():
    usuario  = st.session_state.get("usuario", {})
    horas    = float(usuario.get("horas_por_dia", 3.0))
    dias     = int(usuario.get("dias_semana", 5))
    data_p   = usuario.get("data_prova", "")
    area     = usuario.get("area_estudo", "")

    st.html(
        "<div style='background:linear-gradient(135deg,#061020,#0d1b2a);border-radius:10px;"
        "padding:18px 24px;margin-bottom:16px;text-align:center;border-bottom:3px solid #00b4a6;"
        "box-shadow:0 4px 16px rgba(0,0,0,0.35);'>"
        "<span style='color:#ffffff;font-weight:800;font-size:1.3rem;"
        "letter-spacing:0.12em;text-transform:uppercase;'>Meu Plano Semanal</span>"
        "<div style='color:#7a9ab8;font-size:0.78rem;margin-top:4px;'>"
        "Priorizado por urgência, lacuna e desempenho real</div></div>"
    )

    msg_reforco = st.session_state.pop("_reforco_msg", None)
    if msg_reforco:
        st.warning(f"Reforço inserido: Flashcard adicionado para '{msg_reforco}' (desempenho < 60%).")

    c1, c2, c3 = st.columns(3)
    c1.metric("Carga/semana", f"{int(horas * dias)}h")
    c2.metric("Dias de estudo", f"{dias}")
    c3.metric("Max/sessão", "50 min")
    if data_p:
        st.markdown(
            f"<p style='color:#7a9ab8;font-size:0.82rem;'>Prova: <strong>{data_p}</strong></p>",
            unsafe_allow_html=True,
        )

    if not st.session_state.get("onboarding_concluido") and not area:
        st.divider()
        st.info("Você ainda não configurou seu plano.")
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

    sessoes_por_dia = max(1, int(horas * 60 / 50))
    total_buscar    = min(sessoes_por_dia * dias + 10, 50)

    with st.spinner("Calculando plano..."):
        sessoes = get_agenda(top=total_buscar)

    if not sessoes:
        st.divider()
        st.info("Nenhuma sessão pendente. Conclua o onboarding para gerar seu plano de estudos.")
        if st.button("Ir para Onboarding →", type="primary"):
            st.session_state.ob_tela = 1
            st.session_state.pagina  = "onboarding"
            st.rerun()
        return

    st.divider()
    _render_meta(sessoes, horas, dias)

    col_adiar, _ = st.columns([1, 3])
    with col_adiar:
        if st.button("Adiar Meta (+7 dias)", key="btn_adiar", use_container_width=True):
            if adiar_meta(dias=7):
                st.toast("Meta adiada em 7 dias.")
                for k in list(st.session_state.keys()):
                    if k.startswith("ok_") or k.startswith("exp_"):
                        del st.session_state[k]
                st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    for idx, s in enumerate(sessoes):
        _card(s, idx)

    st.divider()
    if st.button("Recalcular plano", key="btn_recalc"):
        prefixes = ("ok_", "fb_", "exp_", "qr_", "qativo_", "perc_", "dur_")
        for k in list(st.session_state.keys()):
            if any(k.startswith(p) for p in prefixes):
                del st.session_state[k]
        st.rerun()
