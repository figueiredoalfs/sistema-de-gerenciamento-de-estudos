"""
pg_plano.py — Trilha de Aprendizado
Exibe a meta semanal, o hero card da próxima task e a timeline do dia.
"""
import streamlit as st
from api_client import (
    api_get_tasks_hoje,
    api_get_meta_ativa,
    api_listar_tasks,
    api_concluir_task,
    api_iniciar_task,
    api_gerar_meta,
)
from telas.components import page_header, tipo_label, _injetar_css, TIPO_CORES


# ── Componentes de layout ─────────────────────────────────────────────────────

def _render_progress_header(meta: dict | None):
    """Barra de progresso da meta semanal."""
    if not meta:
        return
    total = meta.get("tasks_total", 0)
    concluidas = meta.get("tasks_completed", 0)
    pct = meta.get("progress_percentage", 0)
    cor = "#27ae60" if pct >= 70 else "#f59e0b" if pct >= 40 else "#e74c3c"
    st.markdown(
        f'<div class="progress-header">'
        f'  <div class="progress-title">Meta semanal</div>'
        f'  <div class="progress-value">{concluidas} de {total} tasks concluídas</div>'
        f'  <div class="progress-bar-bg">'
        f'    <div class="progress-bar-fill" style="width:{pct}%;background:{cor};"></div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_hero(task: dict):
    """Card em destaque da próxima task pendente."""
    materia = task.get("subject_nome", "—")
    subtema = task.get("subtopic_nome") or task.get("topic_nome", "—")
    tipo = task.get("tipo", "")
    cor = TIPO_CORES.get(tipo, "#8ab0c8")
    label = tipo_label(tipo)
    st.markdown(
        f'<div class="hero-card">'
        f'  <div class="hero-title">PRÓXIMA TASK</div>'
        f'  <div class="hero-materia">{materia}</div>'
        f'  <div class="hero-subtema">{subtema}</div>'
        f'  <span style="display:inline-block;padding:3px 12px;border-radius:20px;'
        f'background:{cor};color:#fff;font-size:0.78rem;font-weight:700;">{label.upper()}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button("▶ Iniciar Estudo", key=f"hero_iniciar_{task['id']}", type="primary"):
        api_iniciar_task(task["id"])
        st.session_state["timer_task_id"] = task["id"]
        st.rerun()


def _render_timer_inline(task_id: str):
    """Timer embutido dentro do card expandido."""
    tid = task_id.replace("-", "_")
    st.markdown(
        f"""
<div style="background:#0f1e2a;border:1px solid #1e3040;border-radius:8px;padding:10px 16px;
display:flex;align-items:center;gap:16px;font-family:monospace;margin:8px 0 12px 0;">
  <span style="font-size:0.75rem;color:#8ab0c8;">⏱ Cronômetro</span>
  <span id="tdsp_{tid}" style="font-size:1.1rem;font-weight:700;color:#00b4a6;min-width:56px;">00:00</span>
  <button onclick="tt_{tid}()" style="background:#1e3040;border:1px solid #2a4a60;
color:#e8f4ff;padding:3px 12px;border-radius:6px;cursor:pointer;font-size:0.8rem;" id="tbtn_{tid}">▶ Iniciar</button>
  <button onclick="tr_{tid}()" style="background:#1e3040;border:1px solid #2a4a60;
color:#e8f4ff;padding:3px 12px;border-radius:6px;cursor:pointer;font-size:0.8rem;">↺ Reiniciar</button>
</div>
<script>
(function(){{
  var s=0,r=false,iv=null;
  var d=document.getElementById('tdsp_{tid}');
  var b=document.getElementById('tbtn_{tid}');
  function p(n){{return n<10?'0'+n:''+n;}}
  function u(){{var m=Math.floor(s/60),sc=s%60;if(d)d.textContent=p(m)+':'+p(sc);}}
  window.tt_{tid}=function(){{
    if(r){{clearInterval(iv);r=false;if(b)b.textContent='▶ Continuar';}}
    else{{iv=setInterval(function(){{s++;u();}},1000);r=true;if(b)b.textContent='⏸ Pausar';}}
  }};
  window.tr_{tid}=function(){{clearInterval(iv);r=false;s=0;u();if(b)b.textContent='▶ Iniciar';}};
}})();
</script>
""",
        unsafe_allow_html=True,
    )


def _render_trail(tasks: list):
    """Timeline vertical de cards expansíveis."""
    if not tasks:
        st.info("Nenhuma task para hoje. Gere uma nova meta para continuar estudando.")
        return

    for i, task in enumerate(tasks):
        tid = task["id"]
        status = task.get("status", "pending")
        materia = task.get("subject_nome", "—")
        subtema = task.get("subtopic_nome") or task.get("topic_nome", "—")
        tipo = task.get("tipo", "")
        cor_tipo = TIPO_CORES.get(tipo, "#8ab0c8")
        label_tipo = tipo_label(tipo)
        concluida = status == "completed"
        status_css = "completed" if concluida else "pending"
        timer_ativo = st.session_state.get("timer_task_id") == tid
        feito_html = '<span style="color:#27ae60;font-size:0.85rem;margin-left:8px;">✓ Feito</span>' if concluida else ""

        # Card visual
        st.markdown(
            f'<div class="trail-card {status_css}">'
            f'  <div class="trail-card-header">'
            f'    <span class="trail-dot {status_css}"></span>'
            f'    <div style="flex:1;">'
            f'      <span class="trail-materia">{materia}</span>'
            f'      <span style="color:#2a4a60;margin:0 6px;">—</span>'
            f'      <span class="trail-subtema">{subtema}</span>'
            f'    </div>'
            f'    <span style="display:inline-block;padding:2px 9px;border-radius:20px;'
            f'background:{cor_tipo};color:#fff;font-size:0.72rem;font-weight:700;">{label_tipo.upper()}</span>'
            f'    {feito_html}'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Expansão apenas para tasks não concluídas
        if not concluida:
            with st.expander("Ações", expanded=timer_ativo):
                if timer_ativo:
                    _render_timer_inline(tid)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶ Iniciar Estudo", key=f"trail_iniciar_{tid}"):
                        api_iniciar_task(tid)
                        st.session_state["timer_task_id"] = tid
                        st.rerun()
                with col2:
                    if st.button("✓ Concluir", key=f"trail_concluir_{tid}", type="primary"):
                        resultado = api_concluir_task(tid)
                        if st.session_state.get("timer_task_id") == tid:
                            del st.session_state["timer_task_id"]
                        if resultado:
                            geradas = resultado.get("tarefas_geradas") or []
                            if geradas:
                                st.toast(f"✅ {len(geradas)} nova(s) task(s) gerada(s) para você!")
                        st.rerun()

        # Linha conectora entre cards
        if i < len(tasks) - 1:
            st.markdown(
                '<div style="width:2px;height:12px;background:#1e3040;margin-left:4px;"></div>',
                unsafe_allow_html=True,
            )


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    _injetar_css()

    if not st.session_state.get("api_token"):
        page_header("Trilha de Hoje", "")
        st.warning("Sessão expirada. Saia e entre novamente para continuar.")
        if st.button("Sair", key="plano_logout"):
            st.session_state.clear()
            st.rerun()
        return

    page_header("Trilha de Hoje", "Veja seu progresso e conclua as tasks do dia")

    # Progresso da meta semanal
    meta = api_get_meta_ativa()
    _render_progress_header(meta)

    # Tasks do dia
    resultado = api_get_tasks_hoje()
    tasks = resultado.get("tasks", [])

    if not tasks:
        # Checar se há diagnóstico pendente
        diag = api_listar_tasks(tipo="diagnostico", status="pending")
        if diag:
            st.info("Complete o diagnóstico inicial para gerar seu plano de estudos personalizado.")
            if st.button("Fazer Diagnóstico →", type="primary", key="btn_diagnostico"):
                st.session_state.pagina = "meta_00"
                st.rerun()
        else:
            st.info("Todas as tasks concluídas! Gere uma nova meta para continuar.")
            if st.button("🎯 Gerar Nova Meta", type="primary", key="btn_nova_meta"):
                with st.spinner("Gerando nova meta..."):
                    r = api_gerar_meta()
                if r:
                    st.toast("✅ Nova meta criada!")
                    st.rerun()
                else:
                    st.error("Não foi possível gerar nova meta. Verifique se o servidor está rodando.")
        return

    # Hero: próxima task pendente
    proxima = next((t for t in tasks if t.get("status") != "completed"), None)
    if proxima:
        _render_hero(proxima)
        st.markdown("<br>", unsafe_allow_html=True)

    # Contador
    st.markdown(
        f'<div style="font-size:0.8rem;color:#8ab0c8;margin-bottom:8px;">'
        f'Tasks de hoje — {len(tasks)} {"task" if len(tasks) == 1 else "tasks"}</div>',
        unsafe_allow_html=True,
    )

    # Timeline
    _render_trail(tasks)
