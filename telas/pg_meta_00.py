"""
telas/pg_meta_00.py — Diagnóstico Inicial (Meta 00)

Exibe as baterias diagnósticas geradas no onboarding (tipo="diagnostico").
O aluno responde as questões de cada matéria e conclui o diagnóstico.
Ao concluir, o backend calcula o desempenho e gera o plano de estudos adaptado.
"""

import json

import streamlit as st

from api_client import (
    api_concluir_task,
    api_get_questoes_task,
    api_listar_tasks,
    api_responder_questao,
)
from telas.components import page_header, _injetar_css


# ── Helpers ───────────────────────────────────────────────────────────────────

def _barra_progresso(respondidas: int, total: int):
    pct = int(respondidas / total * 100) if total else 0
    cor = "#06d6a0" if pct == 100 else "#3a86ff" if pct >= 50 else "#f77f00"
    st.markdown(
        f'<div style="margin:8px 0 16px 0;">'
        f'  <div style="display:flex;justify-content:space-between;'
        f'font-size:0.8rem;color:#8ab0c8;margin-bottom:4px;">'
        f'    <span>{respondidas} de {total} questões respondidas</span>'
        f'    <span style="color:{cor};font-weight:700;">{pct}%</span>'
        f'  </div>'
        f'  <div style="background:#0a1628;border-radius:6px;height:8px;">'
        f'    <div style="background:{cor};width:{pct}%;height:8px;'
        f'border-radius:6px;transition:width 0.3s;"></div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_questao(q: dict, idx: int, respostas_dadas: dict, task_id: str):
    """Renderiza uma questão com botões de alternativa."""
    qid = q["id"]
    ja_respondida = qid in respostas_dadas
    alternativas: dict = json.loads(q.get("alternativas_json") or "{}")

    with st.container():
        st.markdown(
            f'<div style="background:#0e1d2b;border-radius:10px;padding:16px;margin-bottom:12px;">'
            f'<p style="color:#8ab0c8;font-size:0.75rem;margin:0 0 6px 0;">'
            f'Questão {idx}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(q.get("enunciado", ""), unsafe_allow_html=False)

        if ja_respondida:
            resp = respostas_dadas[qid]
            correta = resp.get("correta", False)
            letra_dada = resp.get("resposta_dada", "")
            gabarito = q.get("resposta_correta", "")
            if correta:
                st.success(f"✅ Correta! Sua resposta: **{letra_dada}**")
            else:
                st.error(f"❌ Errada. Sua resposta: **{letra_dada}** — Gabarito: **{gabarito}**")
        else:
            cols = st.columns(min(len(alternativas), 5))
            for i, (letra, texto) in enumerate(alternativas.items()):
                with cols[i % len(cols)]:
                    label = f"**{letra}**"
                    if st.button(label, key=f"resp_{task_id}_{qid}_{letra}", use_container_width=True):
                        resultado = api_responder_questao(qid, letra)
                        if resultado:
                            resp_key = f"meta00_resps_{task_id}"
                            st.session_state.setdefault(resp_key, {})[qid] = resultado
                            st.rerun()
                        else:
                            st.error("Erro ao registrar resposta. Tente novamente.")

            # Mostra os textos das alternativas abaixo dos botões
            for letra, texto in alternativas.items():
                st.markdown(
                    f'<p style="font-size:0.82rem;color:#c8d6e5;margin:2px 0;">'
                    f'<b style="color:#3a86ff;">{letra})</b> {texto}</p>',
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ── Tela de seleção de matéria ─────────────────────────────────────────────────

def _render_lista_tasks(tasks: list):
    """Mostra cards das matérias diagnósticas pendentes."""
    st.markdown(
        '<div style="background:#0e1d2b;border:1px solid #1e4a6a;border-radius:12px;'
        'padding:20px;margin-bottom:24px;">'
        '<h4 style="color:#3a86ff;margin:0 0 8px 0;">📋 Matérias para diagnosticar</h4>'
        '<p style="color:#8ab0c8;font-size:0.85rem;margin:0;">Clique em uma matéria para iniciar o diagnóstico.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    for task in tasks:
        nome = task.get("subject_nome") or "Matéria"
        tid = task["id"]
        resp_key = f"meta00_resps_{tid}"
        respostas = st.session_state.get(resp_key, {})
        questoes_ids = json.loads(task.get("questoes_json") or "[]")
        total = len(questoes_ids)
        respondidas = len(respostas)
        pct = int(respondidas / total * 100) if total else 0
        cor_pct = "#06d6a0" if pct == 100 else "#f59e0b" if pct > 0 else "#8ab0c8"

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f'<div style="padding:10px 0;">'
                f'<span style="color:#e8f4ff;font-weight:600;">{nome}</span>'
                f' <span style="color:{cor_pct};font-size:0.8rem;margin-left:8px;">'
                f'{respondidas}/{total} respondidas ({pct}%)</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col2:
            label = "Continuar →" if respondidas > 0 else "Iniciar →"
            if st.button(label, key=f"sel_task_{tid}", use_container_width=True, type="primary"):
                st.session_state["meta00_task_atual"] = tid
                st.rerun()


# ── Tela de resposta de questões ──────────────────────────────────────────────

def _render_task(task: dict):
    """Mostra as questões de uma task diagnóstica e permite respondê-las."""
    tid = task["id"]
    subject_nome = task.get("subject_nome") or "Matéria"

    if st.button("← Voltar às matérias", key="meta00_voltar"):
        st.session_state.pop("meta00_task_atual", None)
        st.rerun()

    st.markdown(f"### 🎯 {subject_nome}")

    questoes_ids = json.loads(task.get("questoes_json") or "[]")
    if not questoes_ids:
        st.warning("Nenhuma questão disponível para esta matéria.")
        return

    resp_key = f"meta00_resps_{tid}"
    if resp_key not in st.session_state:
        st.session_state[resp_key] = {}
    respostas_dadas: dict = st.session_state[resp_key]

    # Busca as questões pela API apenas uma vez por task
    cache_key = f"meta00_questoes_{tid}"
    if cache_key not in st.session_state:
        with st.spinner("Carregando questões..."):
            questoes = api_get_questoes_task(tid)
            # Ordena conforme a sequência original do questoes_json
            ordem = {qid: i for i, qid in enumerate(questoes_ids)}
            questoes.sort(key=lambda q: ordem.get(q["id"], 999))
            st.session_state[cache_key] = questoes
    else:
        questoes = st.session_state[cache_key]

    if not questoes:
        st.warning("As questões desta bateria não foram encontradas no banco.")
        return

    respondidas = len(respostas_dadas)
    total = len(questoes)
    _barra_progresso(respondidas, total)

    for i, q in enumerate(questoes, 1):
        _render_questao(q, i, respostas_dadas, tid)

    st.divider()

    if respondidas >= total:
        st.success("✅ Você respondeu todas as questões desta bateria!")
        if st.button(
            "Concluir diagnóstico e gerar plano de estudos",
            type="primary",
            use_container_width=True,
            key=f"concluir_{tid}",
        ):
            with st.spinner("Calculando desempenho e gerando plano..."):
                resultado = api_concluir_task(tid)
            if resultado:
                tarefas = resultado.get("tarefas_geradas") or []
                st.session_state.pop(resp_key, None)
                st.session_state.pop(cache_key, None)
                st.session_state.pop("meta00_task_atual", None)
                if tarefas:
                    st.toast(f"✅ {len(tarefas)} tasks de estudo criadas para {subject_nome}!")
                else:
                    st.toast(f"✅ Diagnóstico de {subject_nome} concluído!")
                st.rerun()
            else:
                st.error("Erro ao concluir o diagnóstico. Tente novamente.")
    else:
        st.info(f"Responda todas as {total} questões para concluir o diagnóstico.")


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    _injetar_css()
    page_header("Diagnóstico Inicial", "Meta 00 — Calibre seu nível antes de começar")

    tasks = api_listar_tasks(tipo="diagnostico", status="pending")

    if not tasks:
        st.success("✅ Todos os diagnósticos foram concluídos! Seu plano de estudos está pronto.")
        if st.button("Ver Agenda de Estudos →", type="primary"):
            st.session_state.pagina = "plano"
            st.rerun()
        return

    task_atual_id = st.session_state.get("meta00_task_atual")
    task_atual = next((t for t in tasks if t["id"] == task_atual_id), None)

    if task_atual:
        _render_task(task_atual)
    else:
        _render_lista_tasks(tasks)
