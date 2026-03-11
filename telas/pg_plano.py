"""
pg_plano.py - Plano semanal priorizado pelo algoritmo de scoring.
"""
import streamlit as st
from database import get_perfil
from api_client import api_get_agenda, api_concluir_sessao

TIPO_LABEL = {"teoria_pdf": "Teoria", "exercicios": "Exercicios", "video": "Video", "flashcard_texto": "Flashcard", "calibracao": "Calibracao"}
TIPO_COR = {"teoria_pdf": "#3b82f6", "exercicios": "#f59e0b", "video": "#8b5cf6", "flashcard_texto": "#10b981", "calibracao": "#00b4a6"}
DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]

def _prio(score):
    if score >= 0.7: return "URGENTE", "#e74c3c"
    elif score >= 0.5: return "Alta", "#f59e0b"
    return "Normal", "#27ae60"

def _montar_semana(sessoes, horas_dia, dias):
    limite = int(horas_dia * 60)
    semana, dia_atual, minutos = [], [], 0
    for s in sessoes:
        dur = min(s.get("duracao_planejada_min", 50), 50)
        s = {**s, "duracao_planejada_min": dur}
        if minutos + dur > limite and dia_atual:
            semana.append(dia_atual)
            dia_atual, minutos = [], 0
            if len(semana) >= dias: break
        dia_atual.append(s)
        minutos += dur
    if dia_atual and len(semana) < dias:
        semana.append(dia_atual)
    return semana

def _card(s, di, ti):
    tipo = s.get("tipo", "")
    tipo_label = TIPO_LABEL.get(tipo, tipo)
    tipo_cor = TIPO_COR.get(tipo, "#7a9ab8")
    score = s.get("score", 0)
    prio_label, prio_cor = _prio(score)
    dur = s.get("duracao_planejada_min", 50)
    topico = s.get("topico_nome", "Topico")
    area = s.get("area", "")
    sid = s.get("sessao_id", "")
    key = f"d{di}_t{ti}_{sid[:8]}"

    if st.session_state.get(f"ok_{sid}"):
        st.html(f"<div style='background:#0a1628;border-radius:8px;border-left:4px solid #27ae60;padding:8px 16px;margin-bottom:6px;opacity:0.5;'><span style='color:#27ae60;font-size:0.75rem;'>Concluido</span> <span style='color:#7a9ab8;font-size:0.82rem;'>{topico[:45]}</span></div>")
        return

    col_info, col_btn = st.columns([4, 1])
    with col_info:
        st.html(f"<div style='background:linear-gradient(135deg,#0a1628,#0d1b2a);border-radius:8px;border:1px solid #1a3050;border-left:4px solid {tipo_cor};padding:12px 16px;'><div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'><span style='background:{tipo_cor}22;color:{tipo_cor};font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;'>{tipo_label}</span><span style='background:{prio_cor}22;color:{prio_cor};font-size:0.65rem;padding:2px 6px;border-radius:4px;font-weight:700;'>{prio_label}</span><span style='color:#7a9ab8;font-size:0.68rem;margin-left:auto;'>{dur} min</span></div><div style='color:#ffffff;font-weight:700;font-size:0.92rem;'>{topico}</div><div style='color:#7a9ab8;font-size:0.75rem;margin-top:2px;'>{area}</div></div>")
    with col_btn:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Concluir", key=f"btn_{key}", use_container_width=True, type="primary"):
            st.session_state[f"fb_{sid}"] = True
            st.rerun()

    if st.session_state.get(f"fb_{sid}"):
        st.markdown(f"<div style='background:#0d1b2a;border:1px solid #00b4a6;border-radius:8px;padding:10px 16px;margin-bottom:6px;'><span style='color:#c8d6e5;font-size:0.82rem;'>Como foi em <b>{topico[:35]}</b>?</span></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        perc = c1.slider("% acerto", 0, 100, 70, key=f"perc_{key}")
        dur_r = c2.number_input("Tempo real (min)", 5, 120, dur, key=f"dur_{key}")
        b1, b2 = st.columns(2)
        if b1.button("Salvar", key=f"salvar_{key}", type="primary"):
            res = api_concluir_sessao(sid, percentual=float(perc), duracao_real_min=int(dur_r))
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"fb_{sid}", None)
            if res and res.get("reforco_inserido"):
                st.session_state["_reforco_msg"] = topico[:35]
            st.rerun()
        if b2.button("Pular", key=f"skip_{key}"):
            api_concluir_sessao(sid, percentual=0, duracao_real_min=0)
            st.session_state[f"ok_{sid}"] = True
            st.session_state.pop(f"fb_{sid}", None)
            st.rerun()

def render():
    usuario_id = st.session_state.usuario["id"]
    perfil = get_perfil(usuario_id)
    area  = perfil.get("area_estudo", "")
    horas = float(perfil.get("horas_dia") or 3.0)
    dias  = int(perfil.get("dias_semana") or 5)
    data_p = perfil.get("data_prova", "")

    st.html("<div style='background:linear-gradient(135deg,#061020,#0d1b2a);border-radius:10px;padding:18px 24px;margin-bottom:20px;text-align:center;border-bottom:3px solid #00b4a6;box-shadow:0 4px 16px rgba(0,0,0,0.35);'><span style='color:#ffffff;font-weight:800;font-size:1.3rem;letter-spacing:0.12em;text-transform:uppercase;'>Meu Plano Semanal</span><div style='color:#7a9ab8;font-size:0.78rem;margin-top:4px;'>Priorizado por urgencia, lacuna e desempenho real</div></div>")

    msg_reforco = st.session_state.pop("_reforco_msg", None)
    if msg_reforco:
        st.warning(f"Reforco inserido: Flashcard adicionado para '{msg_reforco}' (desempenho < 60%).")

    c1, c2, c3 = st.columns(3)
    c1.metric("Carga semanal", f"{int(horas * dias)}h")
    c2.metric("Dias", f"{dias}")
    c3.metric("Max/sessao", "50 min")
    if data_p:
        st.markdown(f"<p style='color:#7a9ab8;font-size:0.82rem;'>Prova: <strong>{data_p}</strong></p>", unsafe_allow_html=True)
    st.divider()

    if not st.session_state.get("api_token"):
        st.warning("Sessao expirada. Faca logout e entre novamente.")
        if st.button("Sair", key="plano_logout"): st.session_state.clear(); st.rerun()
        return

    if not area or perfil.get("plano") != "ativo":
        st.info("Voce ainda nao configurou seu plano.")
        if st.button("Configurar ->", type="primary"):
            st.session_state.ob_tela = 1; st.session_state.pagina = "onboarding"; st.rerun()
        return

    sessoes_por_dia = max(1, int(horas * 60 / 50))
    total_buscar = min(sessoes_por_dia * dias + 10, 50)

    with st.spinner("Calculando plano..."):
        sessoes = api_get_agenda(top=total_buscar)

    if not sessoes:
        st.info("Nenhuma sessao pendente. Use Carregar Dados de Teste para gerar um plano.")
        return

    semana = _montar_semana(sessoes, horas, dias)

    for di, tarefas in enumerate(semana):
        total_min = sum(t.get("duracao_planejada_min", 50) for t in tarefas)
        n_ok = sum(1 for t in tarefas if st.session_state.get(f"ok_{t["sessao_id"]}"))
        st.html(f"<div style='display:flex;justify-content:space-between;background:#061020;border-radius:8px 8px 0 0;padding:8px 16px;border-bottom:2px solid #00b4a6;margin-top:12px;'><span style='color:#ffffff;font-weight:800;'>{DIAS[di % 7]}</span><span style='color:#7a9ab8;font-size:0.75rem;'>{n_ok}/{len(tarefas)} concluidas | {total_min} min</span></div>")
        for ti, s in enumerate(tarefas):
            _card(s, di, ti)

    st.divider()
    if st.button("Recalcular plano", key="btn_recalc"):
        for k in list(st.session_state.keys()):
            if k.startswith("ok_") or k.startswith("fb_"): del st.session_state[k]
        st.rerun()
