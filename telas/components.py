"""
telas/components.py
Componentes reutilizáveis para todas as telas do sistema.

Uso:
    from telas.components import page_header, kpi_card, score_to_stars, tipo_badge, timer_bar
"""

import streamlit as st


# ── Tipos de sessão ───────────────────────────────────────────────────────────

TIPO_LABELS: dict[str, str] = {
    "teoria_pdf":     "Teoria",
    "exercicios":     "Questões",
    "video":          "Vídeo",
    "flashcard_texto":"Revisão",
    "calibracao":     "Calibração",
}

TIPO_CORES: dict[str, str] = {
    "teoria_pdf":     "#3a86ff",
    "exercicios":     "#06d6a0",
    "video":          "#f77f00",
    "flashcard_texto":"#9b5de5",
    "calibracao":     "#8ab0c8",
}


# ── CSS global injetado uma vez por sessão ────────────────────────────────────

_CSS_INJETADO = False

def _injetar_css():
    global _CSS_INJETADO
    if _CSS_INJETADO:
        return
    _CSS_INJETADO = True
    st.markdown("""
    <style>
    /* KPI Cards */
    .kpi-card {
        background: #19293a;
        border-radius: 12px;
        padding: 18px 20px 16px 20px;
        margin-bottom: 4px;
        border-left: 3px solid #00b4a6;
        min-height: 90px;
    }
    .kpi-icon   { font-size: 1.4rem; margin-bottom: 4px; }
    .kpi-valor  { font-size: 1.8rem; font-weight: 700; color: #e8f4ff; line-height: 1.1; }
    .kpi-label  { font-size: 0.78rem; color: #8ab0c8; margin-top: 4px; }

    /* Tipo badge */
    .tipo-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #fff;
    }
    .tipo-teoria_pdf      { background: #3a86ff; }
    .tipo-exercicios      { background: #06d6a0; color: #0a1520; }
    .tipo-video           { background: #f77f00; }
    .tipo-flashcard_texto { background: #9b5de5; }
    .tipo-calibracao      { background: #8ab0c8; color: #0a1520; }

    /* Meta progress */
    .meta-card {
        background: #19293a;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    .meta-tag {
        display: inline-block;
        background: #0f2a3a;
        border: 1px solid #00b4a6;
        color: #00b4a6;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 10px;
        margin-bottom: 8px;
    }
    .meta-info { font-size: 0.78rem; color: #8ab0c8; margin-top: 6px; }

    /* Próxima meta / painel lateral */
    .prox-card {
        background: #19293a;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        text-align: center;
    }
    .prox-titulo { font-size: 0.8rem; color: #8ab0c8; margin-bottom: 8px; }
    .prox-data   { font-size: 1.2rem; font-weight: 700; color: #00b4a6; }

    /* Tabela de atividades — linhas alternadas */
    .row-atividade {
        padding: 8px 0;
        border-bottom: 1px solid #1e3040;
    }
    .row-atividade:hover { background: #1a2d3d; }

    /* Header de página */
    .page-header-nome  { font-size: 1.6rem; font-weight: 700; color: #e8f4ff; }
    .page-header-sub   { font-size: 0.85rem; color: #8ab0c8; margin-top: -4px; }

    /* Timer bar no topo */
    #timer-bar {
        position: fixed;
        top: 0; left: 0; right: 0;
        background: #0f1e2a;
        border-bottom: 1px solid #1e3040;
        padding: 6px 20px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 16px;
        font-family: monospace;
    }
    #timer-display { font-size: 1.1rem; font-weight: 700; color: #00b4a6; min-width: 70px; }
    .timer-btn {
        background: #1e3040;
        border: 1px solid #2a4a60;
        color: #e8f4ff;
        padding: 3px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.8rem;
    }
    .timer-btn:hover { background: #2a4a60; }
    .timer-label { font-size: 0.75rem; color: #8ab0c8; }
    </style>
    """, unsafe_allow_html=True)


# ── Componentes públicos ──────────────────────────────────────────────────────

def page_header(titulo: str, subtitulo: str = ""):
    """Header padrão de página com título e subtítulo."""
    _injetar_css()
    nome = st.session_state.get("usuario", {}).get("nome", "")
    primeiro_nome = nome.split()[0] if nome else ""
    greeting = f"Oi, {primeiro_nome}" if primeiro_nome else titulo
    st.markdown(
        f'<div class="page-header-nome">{greeting}</div>'
        f'<div class="page-header-sub">{subtitulo}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)


def page_title(titulo: str, subtitulo: str = ""):
    """Header de página sem saudação — para telas que não são a principal."""
    _injetar_css()
    st.markdown(
        f'<div class="page-header-nome">{titulo}</div>'
        f'<div class="page-header-sub">{subtitulo}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)


def kpi_card(label: str, valor: str, icone: str = "", cor_borda: str = "#00b4a6"):
    """Card KPI compacto padronizado."""
    _injetar_css()
    st.markdown(
        f'<div class="kpi-card" style="border-left-color:{cor_borda};">'
        f'  <div class="kpi-icon">{icone}</div>'
        f'  <div class="kpi-valor">{valor}</div>'
        f'  <div class="kpi-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def score_to_stars(score: float) -> str:
    """Converte score 0–1 em string de estrelas (★★★★☆)."""
    n = round(score * 5)
    n = max(0, min(5, n))
    return "★" * n + "☆" * (5 - n)


def tipo_badge(tipo: str) -> str:
    """Retorna HTML de badge colorido para o tipo de sessão."""
    label = TIPO_LABELS.get(tipo, tipo)
    return f'<span class="tipo-badge tipo-{tipo}">{label}</span>'


def tipo_label(tipo: str) -> str:
    """Retorna label legível para o tipo de sessão."""
    return TIPO_LABELS.get(tipo, tipo)


def timer_bar() -> str:
    """Retorna HTML+JS do timer de estudo fixo no topo da página."""
    return """
<div id="timer-bar">
  <span class="timer-label">⏱ Cronômetro</span>
  <span id="timer-display">00:00</span>
  <button class="timer-btn" onclick="timerToggle()">▶ Iniciar</button>
  <button class="timer-btn" onclick="timerReset()">↺ Reiniciar</button>
  <span id="timer-status" class="timer-label"></span>
</div>
<script>
(function() {
  var _s = 0, _running = false, _iv = null;
  function pad(n) { return n < 10 ? '0'+n : ''+n; }
  function update() {
    var m = Math.floor(_s/60), sec = _s%60;
    document.getElementById('timer-display').textContent = pad(m)+':'+pad(sec);
  }
  window.timerToggle = function() {
    if (_running) {
      clearInterval(_iv); _running = false;
      document.querySelector('#timer-bar .timer-btn').textContent = '▶ Continuar';
      document.getElementById('timer-status').textContent = 'pausado';
    } else {
      _iv = setInterval(function(){ _s++; update(); }, 1000);
      _running = true;
      document.querySelector('#timer-bar .timer-btn').textContent = '⏸ Pausar';
      document.getElementById('timer-status').textContent = '';
    }
  };
  window.timerReset = function() {
    clearInterval(_iv); _running = false; _s = 0; update();
    document.querySelector('#timer-bar .timer-btn').textContent = '▶ Iniciar';
    document.getElementById('timer-status').textContent = '';
  };
})();
</script>
<style>body { margin-top: 44px !important; }</style>
"""
