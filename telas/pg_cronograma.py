"""
pg_cronograma.py — Cronograma Semanal
Exibe as tasks de estudo do aluno em formato de cards expandíveis.
"""
import streamlit as st

from api_client import (
    api_listar_cronograma,
    api_obter_task_conteudo,
    api_gerar_pdf_task,
    api_listar_videos_task,
    api_buscar_videos_task,
    api_avaliar_video,
)
from telas.components import page_title, task_card_fechado, TIPO_LABELS, _injetar_css

# Tipos que são pura bateria de questões (sem teoria nem PDF)
_TIPOS_QUESTOES = {"questionario", "simulado", "questions"}

# Quantidade de questões por tipo
_QTDE_QUESTOES: dict[str, int | None] = {
    "questionario": 5,
    "reforco":      10,
    "simulado":     None,  # sem limite fixo
}


# ── Painel de vídeos ──────────────────────────────────────────────────────────

def _render_videos_panel(task_id: str, task_code: str):
    vid_cache = f"videos_{task_code}"
    if vid_cache not in st.session_state:
        st.session_state[vid_cache] = api_listar_videos_task(task_code)

    videos = st.session_state.get(vid_cache, [])

    if not videos:
        c1, c2 = st.columns([3, 1])
        c1.info("Nenhum vídeo cadastrado ainda.")
        with c2:
            if st.button("Buscar com IA", key=f"buscar_vid_{task_id}"):
                with st.spinner("Buscando vídeos..."):
                    videos = api_buscar_videos_task(task_code)
                st.session_state[vid_cache] = videos
                st.rerun()
        return

    for v in videos:
        vid_id = v["id"]
        c_t, c_u, c_n, c_b = st.columns([3, 2, 1, 1])
        c_t.markdown(f"**{v['titulo'][:60]}**")
        c_u.markdown(f"[Assistir]({v['url']})")
        nota = c_n.selectbox(
            "Nota",
            options=[1, 2, 3, 4, 5],
            index=max(0, round(v.get("avaliacao_media", 3)) - 1),
            key=f"nota_vid_{vid_id}",
            label_visibility="collapsed",
        )
        with c_b:
            if st.button("✓", key=f"aval_{vid_id}", help="Salvar avaliação"):
                api_avaliar_video(vid_id, nota)
                del st.session_state[vid_cache]
                st.rerun()

    if st.button("Buscar mais vídeos", key=f"mais_vid_{task_id}"):
        with st.spinner("Buscando..."):
            novos = api_buscar_videos_task(task_code)
        st.session_state[vid_cache] = novos
        st.rerun()


# ── Card individual ───────────────────────────────────────────────────────────

def _render_task_card(task: dict, numero: int):
    task_id   = task["id"]
    task_code = task.get("task_code", "")
    tipo      = task.get("tipo", "")
    status    = task.get("status", "pending")
    expand_key = f"expanded_{task_id}"

    # Cor da borda baseada no status
    cor_borda = "#27ae60" if status == "completed" else "#00b4a6"

    # Card fechado (HTML estático)
    html = task_card_fechado(task, numero)
    # Ajusta cor da borda via inline style override
    html = html.replace('class="task-card"', f'class="task-card" style="border-left-color:{cor_borda};"', 1)
    st.markdown(html, unsafe_allow_html=True)

    # Botão expandir/fechar
    expanded = st.session_state.get(expand_key, False)
    col_btn, _ = st.columns([1, 9])
    with col_btn:
        lbl = "▲ Fechar" if expanded else "▼ Ver"
        if st.button(lbl, key=f"exp_{task_id}"):
            st.session_state[expand_key] = not expanded
            st.rerun()

    if not expanded:
        return

    # ── Conteúdo expandido ────────────────────────────────────────────────────
    with st.container():
        st.markdown(
            '<div style="background:#0f1e2a;border-radius:0 0 10px 10px;'
            'padding:16px 18px;margin-top:-4px;margin-bottom:8px;">',
            unsafe_allow_html=True,
        )

        # Carregar conteúdo (cache)
        cache_key = f"conteudo_{task_code}"
        if cache_key not in st.session_state and task_code:
            with st.spinner("Carregando conteúdo..."):
                data = api_obter_task_conteudo(task_code)
            st.session_state[cache_key] = data or {}

        conteudo = st.session_state.get(cache_key, {})

        if conteudo.get("objetivo"):
            st.markdown(
                f'<p style="font-size:0.85rem;color:#c8d6e5;margin-bottom:4px;">'
                f'<b>Objetivo:</b> {conteudo["objetivo"]}</p>',
                unsafe_allow_html=True,
            )
        if conteudo.get("instrucoes"):
            st.markdown(
                f'<p style="font-size:0.82rem;color:#8ab0c8;margin-bottom:12px;">'
                f'<b>Instruções:</b> {conteudo["instrucoes"]}</p>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="border-color:#1e3040;margin:8px 0;">', unsafe_allow_html=True)

        # ── Botões por tipo ───────────────────────────────────────────────────
        if tipo in _TIPOS_QUESTOES:
            # Apenas bateria de questões
            n = _QTDE_QUESTOES.get(tipo)
            label_n = f" ({n} questões)" if n else ""
            tipo_lbl = TIPO_LABELS.get(tipo, tipo)
            if st.button(f"⚡ Iniciar {tipo_lbl}{label_n}", key=f"iniciar_{task_id}", type="primary"):
                st.session_state["task_cronograma_id"] = task_id
                st.session_state.pagina = "meta_00"
                st.rerun()

        else:
            # Teoria / Revisão / Reforço: vídeo + PDF + questionário
            col_v, col_p = st.columns(2)

            with col_v:
                show_vid = st.session_state.get(f"show_vid_{task_id}", False)
                lbl_vid = "📹 Fechar Vídeos" if show_vid else "📹 Videoaula"
                if st.button(lbl_vid, key=f"vid_{task_id}"):
                    st.session_state[f"show_vid_{task_id}"] = not show_vid
                    st.rerun()

            with col_p:
                if st.button("📄 Gerar PDF", key=f"pdf_{task_id}"):
                    with st.spinner("Gerando material..."):
                        pdf = api_gerar_pdf_task(task_code)
                    st.session_state[f"pdf_{task_code}"] = pdf
                    st.rerun()

            # Painel de vídeos
            if st.session_state.get(f"show_vid_{task_id}"):
                st.markdown("**Vídeos sugeridos:**")
                _render_videos_panel(task_id, task_code)

            # PDF gerado
            pdf_content = st.session_state.get(f"pdf_{task_code}")
            if pdf_content:
                st.markdown("---")
                st.markdown(pdf_content)

            # Questionário de validação (obrigatório para finalizar)
            st.markdown("---")
            st.markdown(
                '<p style="font-size:0.8rem;color:#8ab0c8;">Para finalizar esta task:</p>',
                unsafe_allow_html=True,
            )
            n_q = 10 if tipo == "reforco" else 5
            if st.button(
                f"✍️ Responder Questionário ({n_q} questões)",
                key=f"quiz_{task_id}",
                type="primary",
            ):
                st.session_state["task_cronograma_id"] = task_id
                st.session_state.pagina = "meta_00"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    _injetar_css()
    page_title("Cronograma Semanal", "Suas tarefas de estudo da semana")

    if not st.session_state.get("api_token"):
        st.warning("Sessão expirada. Saia e entre novamente.")
        return

    with st.spinner("Carregando cronograma..."):
        tasks = api_listar_cronograma()

    if not tasks:
        st.info("Nenhuma tarefa no cronograma ainda. Complete o diagnóstico para gerar seu plano de estudos.")
        if st.button("Fazer Diagnóstico →", type="primary"):
            st.session_state.pagina = "meta_00"
            st.rerun()
        return

    # Contadores de status
    total     = len(tasks)
    concluidas = sum(1 for t in tasks if t.get("status") == "completed")
    pendentes  = total - concluidas

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de tasks", total)
    c2.metric("Concluídas", concluidas)
    c3.metric("Pendentes", pendentes)

    st.markdown("<br>", unsafe_allow_html=True)

    for i, task in enumerate(tasks, 1):
        _render_task_card(task, i)
