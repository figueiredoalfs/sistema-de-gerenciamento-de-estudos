"""
pg_agenda.py
Agenda de estudos priorizada pelo algoritmo de scoring.
Mostra top-5 sessoes com score_breakdown (urgencia, lacuna, peso, erros).
"""

import streamlit as st
from api_client import api_get_agenda

TIPO_LABEL = {
    "teoria_pdf":      "Teoria (PDF)",
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

CONF_COR = {
    "baixa":  "#e74c3c",
    "media":  "#f39c12",
    "alta":   "#27ae60",
}


def _score_bar(valor: float, cor: str, label: str) -> str:
    pct = int(valor * 100)
    return f"""
    <div style="margin-bottom:6px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
            <span style="color:#7a9ab8;font-size:0.72rem;letter-spacing:0.05em;">{label}</span>
            <span style="color:#c8d6e5;font-size:0.72rem;font-weight:700;">{pct}%</span>
        </div>
        <div style="background:#0a1628;border-radius:4px;height:6px;">
            <div style="background:{cor};width:{pct}%;height:6px;border-radius:4px;"></div>
        </div>
    </div>
    """


def _card_sessao(idx: int, s: dict) -> str:
    tipo = s.get("tipo", "")
    tipo_label = TIPO_LABEL.get(tipo, tipo)
    tipo_cor = TIPO_COR.get(tipo, "#7a9ab8")
    conf = s.get("confianca", "baixa")
    conf_cor = CONF_COR.get(conf, "#7a9ab8")
    score_pct = int(s.get("score", 0) * 100)
    duracao = s.get("duracao_planejada_min", 0)
    topico = s.get("topico_nome", "Topico geral")
    area = s.get("area", "")

    bd = s.get("score_breakdown", {})
    bars = (
        _score_bar(bd.get("urgencia", 0),    "#e74c3c", "Urgencia")
        + _score_bar(bd.get("lacuna", 0),    "#f59e0b", "Lacuna")
        + _score_bar(bd.get("peso", 0),      "#3b82f6", "Peso Edital")
        + _score_bar(bd.get("fator_erros", 0), "#e67e22", "Fator Erros")
    )

    return f"""
    <div style="
        background:linear-gradient(135deg,#0a1628 0%,#0d1b2a 100%);
        border-radius:10px;
        border:1px solid #1a3050;
        border-left:4px solid {tipo_cor};
        padding:16px 18px;
        margin-bottom:12px;
        box-shadow:0 4px 14px rgba(0,0,0,0.3);
    ">
        <!-- Cabecalho -->
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                    <span style="
                        background:{tipo_cor}22;
                        color:{tipo_cor};
                        font-size:0.7rem;
                        font-weight:700;
                        padding:2px 8px;
                        border-radius:4px;
                        letter-spacing:0.06em;
                    ">{tipo_label}</span>
                    <span style="
                        background:{conf_cor}22;
                        color:{conf_cor};
                        font-size:0.68rem;
                        padding:2px 6px;
                        border-radius:4px;
                    ">conf. {conf}</span>
                </div>
                <div style="color:#ffffff;font-weight:800;font-size:1rem;">{topico}</div>
                <div style="color:#7a9ab8;font-size:0.78rem;margin-top:2px;">{area}</div>
            </div>
            <div style="text-align:right;min-width:80px;">
                <div style="
                    color:#00b4a6;
                    font-size:1.6rem;
                    font-weight:900;
                    line-height:1;
                ">{score_pct}</div>
                <div style="color:#7a9ab8;font-size:0.68rem;">score</div>
                <div style="color:#c8d6e5;font-size:0.8rem;margin-top:4px;">{duracao} min</div>
            </div>
        </div>
        <!-- Breakdown -->
        <div style="border-top:1px solid #1a3050;padding-top:10px;">
            {bars}
        </div>
    </div>
    """


def render():
    st.html("""
        <div style="
            background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;
            padding:18px 24px;
            margin-bottom:20px;
            text-align:center;
            border-bottom:3px solid #00b4a6;
            box-shadow:0 4px 16px rgba(0,0,0,0.35);
        ">
            <span style="
                color:#ffffff;
                font-weight:800;
                font-size:1.3rem;
                letter-spacing:0.12em;
                text-transform:uppercase;
            ">Agenda de Estudos</span>
            <div style="color:#7a9ab8;font-size:0.78rem;margin-top:4px;">
                Top sessoes priorizadas pelo algoritmo de scoring
            </div>
        </div>
    """)

    col_top, _ = st.columns([1, 3])
    with col_top:
        top = st.selectbox("Qtd sessoes", [5, 10, 15], key="agenda_top",
                           label_visibility="collapsed")

    if not st.session_state.get("api_token"):
        st.warning("Sessao expirada. Faca logout e entre novamente para carregar a agenda.")
        if st.button("Sair e relogar", key="agenda_logout"):
            st.session_state.clear()
            st.rerun()
        return

    with st.spinner("Calculando prioridades..."):
        sessoes = api_get_agenda(top=top)

    if not sessoes:
        st.info(
            "Nenhuma sessao pendente encontrada. "
            "Conclua o onboarding para gerar seu cronograma."
        )
        return

    st.html(f"""
        <div style="color:#7a9ab8;font-size:0.8rem;margin-bottom:12px;">
            {len(sessoes)} sessoes · ordenadas por prioridade
        </div>
    """)

    cards_html = "".join(_card_sessao(i, s) for i, s in enumerate(sessoes))
    st.html(f'<div style="max-width:720px;">{cards_html}</div>')

    st.html("""
        <div style="
            background:#0d1b2a;
            border-radius:8px;
            border:1px solid #1a3050;
            padding:12px 16px;
            margin-top:8px;
            font-size:0.74rem;
            color:#7a9ab8;
            line-height:1.6;
        ">
            <b style="color:#c8d6e5;">Como o score e calculado:</b><br>
            Score = 0.35*Urgencia + 0.30*Lacuna + 0.20*Peso + 0.15*FatorErros<br>
            <span style="color:#e74c3c;">Urgencia</span> = pressao do tempo ate a prova &nbsp;|&nbsp;
            <span style="color:#f59e0b;">Lacuna</span> = deficit de conhecimento + esquecimento (decay) &nbsp;|&nbsp;
            <span style="color:#3b82f6;">Peso</span> = importancia no edital &nbsp;|&nbsp;
            <span style="color:#e67e22;">Fator Erros</span> = erros criticos pendentes no topico
        </div>
    """)
