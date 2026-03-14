"""
telas/pg_onboarding.py
Fluxo de onboarding — 4 telas, < 2 minutos.

Tela 1: área do concurso (apenas fiscal)
Tela 2: fase de estudo (pre_edital / pos_edital)
Tela 3: experiência (iniciante / tempo_de_estudo)
Tela 4: funcionalidades desejadas
"""

import requests as _requests
import streamlit as st

_API_BASE = "http://localhost:8000"

FUNCIONALIDADES = [
    ("geracao_conteudo",  "📖", "Geração de Conteúdo",   "Resumos e materiais gerados por IA"),
    ("analise_desempenho","📊", "Análise de Desempenho",  "Relatórios de acertos e pontos fracos"),
    ("cronograma_estudo", "📅", "Cronograma de Estudo",   "Plano de estudos adaptado ao seu ritmo"),
    ("geracao_questoes",  "✏️", "Geração de Questões",    "Questões inéditas geradas por IA"),
]

TEMPOS = [
    ("<1m",  "Menos de 1 mês"),
    ("1-3m", "1 a 3 meses"),
    ("3-6m", "3 a 6 meses"),
    (">6m",  "Mais de 6 meses"),
]

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
<style>
[data-testid="stSidebar"]    { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding-top: 2rem !important;
}
.stApp { background: linear-gradient(160deg,#0a1520 0%,#0f1e2a 100%) !important; }

/* Cards de seleção */
div[data-testid="stButton"] button.ob-card {
    min-height: 160px !important;
    height: auto !important;
    border-radius: 16px !important;
    white-space: pre-wrap !important;
    padding: 24px 16px !important;
    line-height: 1.6 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border: 1.5px solid #1e4a6a !important;
    background: #19293a !important;
    color: #e8f4ff !important;
    transition: border-color 0.15s, background 0.15s !important;
}
div[data-testid="stButton"] button.ob-card-ativo {
    min-height: 160px !important;
    height: auto !important;
    border-radius: 16px !important;
    white-space: pre-wrap !important;
    padding: 24px 16px !important;
    line-height: 1.6 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border: 2px solid #00b4a6 !important;
    background: #0d2535 !important;
    color: #00b4a6 !important;
}
</style>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _step_indicator(atual: int, total: int = 4):
    pontos = ""
    for i in range(1, total + 1):
        if i < atual:
            cor, txt_cor = "#00b4a6", "#fff"
            sombra = ""
        elif i == atual:
            cor, txt_cor = "#00b4a6", "#fff"
            sombra = "box-shadow:0 0 0 3px #00b4a630;"
        else:
            cor, txt_cor = "#19293a", "#3a6080"
            sombra = ""
        pontos += (
            f'<span style="display:inline-block;width:28px;height:28px;border-radius:50%;'
            f'background:{cor};color:{txt_cor};text-align:center;line-height:28px;'
            f'font-size:0.78rem;font-weight:700;margin:0 4px;{sombra}">{i}</span>'
        )
    st.markdown(
        f'<div style="text-align:center;margin-bottom:24px;">{pontos}</div>',
        unsafe_allow_html=True,
    )


def _titulo(emoji: str, titulo: str, sub: str = ""):
    st.markdown(
        f'<div style="text-align:center;margin-bottom:24px;">'
        f'<div style="font-size:2.2rem;margin-bottom:6px;">{emoji}</div>'
        f'<h2 style="color:#e8f4ff;margin:0 0 4px 0;">{titulo}</h2>'
        + (f'<p style="color:#8ab0c8;font-size:0.9rem;margin:0;">{sub}</p>' if sub else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def _card_btn(chave: str, emoji: str, titulo: str, desc: str, ativo: bool, btn_key: str) -> bool:
    """Renderiza um botão no estilo card e retorna True se clicado."""
    check = "  ✓" if ativo else ""
    label = f"{emoji}\n{titulo}\n{desc}{check}"
    css = "ob-card-ativo" if ativo else "ob-card"
    # Injeta classe via markdown antes do botão (hack CSS :has() alternativo)
    st.markdown(f'<style>#{btn_key} button {{ }}</style>', unsafe_allow_html=True)
    clicked = st.button(label, key=btn_key, use_container_width=True)
    return clicked


def _nav(tela_anterior: int | None, tela_proxima: int | None, label_avancar: str = "Continuar →"):
    """Botões de navegação Voltar / Continuar."""
    cols = st.columns([1, 1] if tela_anterior else [1])
    if tela_anterior is not None:
        with cols[0]:
            if st.button("← Voltar", key=f"nav_voltar_{tela_anterior}", use_container_width=True):
                st.session_state.ob_tela = tela_anterior
                st.rerun()
    if tela_proxima is not None:
        col_av = cols[-1]
        with col_av:
            if st.button(label_avancar, key=f"nav_avancar_{tela_proxima}", use_container_width=True, type="primary"):
                return True
    return False


# ── Tela 1 — Área do concurso ─────────────────────────────────────────────────

def _tela1():
    _step_indicator(1)
    _titulo("🎯", "Área do concurso", "Selecione a área que você está estudando")

    # Apenas fiscal disponível por enquanto
    ativo = st.session_state.get("ob_area") == "fiscal"
    col = st.columns([1, 2, 1])[1]
    with col:
        if _card_btn("fiscal", "🏛️", "Fiscal", "Receita Federal, SEFAZ, Auditor...", ativo, "ob_btn_fiscal"):
            st.session_state.ob_area = "fiscal"
            st.session_state.ob_tela = 2
            st.rerun()

    st.markdown(
        '<p style="text-align:center;color:#3a6080;font-size:0.8rem;margin-top:12px;">'
        'Outras áreas em breve</p>',
        unsafe_allow_html=True,
    )


# ── Tela 2 — Fase de estudo ───────────────────────────────────────────────────

def _tela2():
    _step_indicator(2)
    _titulo("📋", "Qual é a sua fase de estudo?")

    fase = st.session_state.get("ob_fase_estudo")
    col1, col2 = st.columns(2)

    with col1:
        if _card_btn("pre_edital", "🌱", "Pré-edital", "Ainda não há edital publicado — estudo base da área", fase == "pre_edital", "ob_btn_pre"):
            st.session_state.ob_fase_estudo = "pre_edital"
            st.rerun()

    with col2:
        if _card_btn("pos_edital", "📄", "Pós-edital", "Edital publicado — foco nas matérias do concurso", fase == "pos_edital", "ob_btn_pos"):
            st.session_state.ob_fase_estudo = "pos_edital"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    avancar = _nav(tela_anterior=1, tela_proxima=3)
    if avancar:
        if not fase:
            st.warning("Selecione uma fase antes de continuar.")
        else:
            st.session_state.ob_tela = 3
            st.rerun()


# ── Tela 3 — Experiência ──────────────────────────────────────────────────────

def _tela3():
    _step_indicator(3)
    _titulo("🎓", "Qual é a sua experiência?", "Isso ajuda a calibrar o nível do seu plano de estudos")

    exp = st.session_state.get("ob_experiencia")
    col1, col2 = st.columns(2)

    with col1:
        if _card_btn("iniciante", "🌱", "Estou começando", "Nunca estudei para este concurso", exp == "iniciante", "ob_btn_ini"):
            st.session_state.ob_experiencia = "iniciante"
            st.session_state.ob_tempo_estudo = None
            st.rerun()

    with col2:
        if _card_btn("tempo_de_estudo", "📚", "Já estudo há algum tempo", "Informe há quanto tempo para calibrar seu nível", exp == "tempo_de_estudo", "ob_btn_tempo"):
            st.session_state.ob_experiencia = "tempo_de_estudo"
            st.rerun()

    if exp == "tempo_de_estudo":
        st.markdown("<br>", unsafe_allow_html=True)
        opcoes_label = [t[1] for t in TEMPOS]
        opcoes_val   = [t[0] for t in TEMPOS]
        atual = st.session_state.get("ob_tempo_estudo", "<1m")
        idx = opcoes_val.index(atual) if atual in opcoes_val else 0
        sel = st.selectbox(
            "Há quanto tempo estuda para este concurso?",
            options=opcoes_label,
            index=idx,
            key="ob_sel_tempo",
        )
        st.session_state.ob_tempo_estudo = opcoes_val[opcoes_label.index(sel)]

    st.markdown("<br>", unsafe_allow_html=True)
    avancar = _nav(tela_anterior=2, tela_proxima=4)
    if avancar:
        if not exp:
            st.warning("Selecione uma opção antes de continuar.")
        elif exp == "tempo_de_estudo" and not st.session_state.get("ob_tempo_estudo"):
            st.warning("Informe há quanto tempo estuda.")
        else:
            st.session_state.ob_tela = 4
            st.rerun()


# ── Tela 4 — Funcionalidades ──────────────────────────────────────────────────

def _tela4():
    _step_indicator(4)
    _titulo("⚙️", "O que você quer usar?", "Selecione as funcionalidades desejadas (pode alterar depois)")

    selecionadas: set = set(st.session_state.get("ob_funcionalidades", []))

    col1, col2 = st.columns(2)
    cols = [col1, col2]

    for i, (chave, emoji, titulo, desc) in enumerate(FUNCIONALIDADES):
        ativo = chave in selecionadas
        with cols[i % 2]:
            if _card_btn(chave, emoji, titulo, desc, ativo, f"ob_func_{chave}"):
                if ativo:
                    selecionadas.discard(chave)
                else:
                    selecionadas.add(chave)
                st.session_state.ob_funcionalidades = list(selecionadas)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_v, col_n = st.columns([1, 1])
    with col_v:
        if st.button("← Voltar", key="nav_voltar_3", use_container_width=True):
            st.session_state.ob_tela = 3
            st.rerun()
    with col_n:
        if st.button("Concluir →", key="ob_concluir", use_container_width=True, type="primary"):
            if not selecionadas:
                st.warning("Selecione ao menos uma funcionalidade.")
            else:
                _enviar_onboarding(list(selecionadas))


# ── Envio para a API ──────────────────────────────────────────────────────────

def _enviar_onboarding(funcionalidades: list):
    token = st.session_state.get("api_token", "")
    exp   = st.session_state.get("ob_experiencia", "iniciante")

    payload = {
        "area":          st.session_state.get("ob_area", "fiscal"),
        "fase_estudo":   st.session_state.get("ob_fase_estudo"),
        "experiencia":   exp,
        "funcionalidades": funcionalidades,
    }
    if exp == "tempo_de_estudo":
        payload["tempo_estudo"] = st.session_state.get("ob_tempo_estudo", "<1m")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        with st.spinner("Criando seu plano de estudos..."):
            r = _requests.post(
                f"{_API_BASE}/onboarding",
                json=payload,
                headers=headers,
                timeout=15,
            )
        if r.status_code == 201:
            dados = r.json()
            st.session_state["perfil_estudo_id"] = dados.get("perfil_estudo_id")
            tasks_geradas = dados.get("tasks_geradas", 0)
            st.session_state.onboarding_concluido = True
            # Marca plano como ativo no banco SQLite local
            from database import salvar_perfil
            salvar_perfil(st.session_state.usuario["id"], {"plano": "ativo"})
            # Limpa estado do onboarding
            for k in list(st.session_state.keys()):
                if k.startswith("ob_"):
                    del st.session_state[k]
            st.session_state.pagina = "plano"
            if tasks_geradas:
                st.toast(f"✅ Plano criado com {tasks_geradas} tasks de estudo!")
            st.rerun()
        else:
            st.error(f"Erro ao salvar perfil ({r.status_code}). Tente novamente.")
    except Exception as e:
        st.error(f"Não foi possível conectar à API. Verifique se o servidor está rodando.\n{e}")


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    if "ob_area" not in st.session_state:
        st.session_state.ob_area = "fiscal"
        st.session_state.ob_tela = 1

    tela = st.session_state.get("ob_tela", 1)

    st.markdown('<div style="padding:0 0 40px 0;">', unsafe_allow_html=True)

    if tela == 1:
        _tela1()
    elif tela == 2:
        _tela2()
    elif tela == 3:
        _tela3()
    elif tela == 4:
        _tela4()

    st.markdown("</div>", unsafe_allow_html=True)
