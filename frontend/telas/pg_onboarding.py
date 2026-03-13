"""
frontend/telas/pg_onboarding.py
Fluxo de onboarding — 6 telas, < 3 minutos.
Dados exclusivamente via API (sem database.py).

Tela 1: seleção de área
Tela 2: edital + data da prova
Tela 3: perfil de estudo (zero / tempo / csv)
Tela 4: plataformas de questões
Tela 5: disponibilidade (horas/dia e dias/semana)
Tela 6: plano gerado — call API onboarding
"""

import os
import sys
import datetime
import streamlit as st
import streamlit.components.v1 as components
from api_client import onboarding as api_onboarding

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config_fontes import GRUPOS_OPCIONAIS, GRUPOS_FONTE, PLATAFORMAS_DEFAULT
from config_materias import MATERIAS_POR_AREA

AREAS = [
    ("fiscal",   "Fiscal",   "🏛️"),
    ("juridica", "Jurídica", "⚖️"),
    ("policial", "Policial", "🚔"),
    ("ti",       "TI",       "💻"),
    ("saude",    "Saúde",    "🏥"),
    ("outro",    "Outro",    "📋"),
]
AREA_LABEL = {k: v for k, v, _ in AREAS}
AREA_API   = {  # slug → valor aceito pelo backend
    "fiscal":   "Fiscal",
    "juridica": "Jurídica",
    "policial": "Policial",
    "ti":       "TI",
    "saude":    "Saúde",
    "outro":    "Outro",
}

TEMPOS = [
    ("<1m",  "Menos de 1 mês",  1),
    ("1-3m", "1 a 3 meses",     2),
    ("3-6m", "3 a 6 meses",     3),
    (">6m",  "Mais de 6 meses", 4),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _step_indicator(atual: int, total: int = 6):
    pontos = ""
    for i in range(1, total + 1):
        if i < atual:
            cor = "#00b4a6"
            pontos += f'<span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:{cor};color:#fff;text-align:center;line-height:28px;font-size:0.75rem;font-weight:700;margin:0 4px;">{i}</span>'
        elif i == atual:
            cor = "#00b4a6"
            pontos += f'<span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:{cor};color:#fff;text-align:center;line-height:28px;font-size:0.85rem;font-weight:700;margin:0 4px;box-shadow:0 0 0 3px #00b4a630;">{i}</span>'
        else:
            pontos += f'<span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:#19293a;color:#3a6080;text-align:center;line-height:28px;font-size:0.75rem;font-weight:600;margin:0 4px;">{i}</span>'
    st.markdown(f'<div style="text-align:center;margin-bottom:24px;">{pontos}</div>', unsafe_allow_html=True)


def _card_titulo(emoji: str, titulo: str, subtitulo: str = ""):
    st.markdown(
        f'<div style="text-align:center;margin-bottom:20px;">'
        f'<div style="font-size:2.4rem;margin-bottom:6px;">{emoji}</div>'
        f'<h2 style="color:#e8f4ff;margin:0 0 4px 0;">{titulo}</h2>'
        + (f'<p style="color:#8ab0c8;font-size:0.9rem;margin:0;">{subtitulo}</p>' if subtitulo else "")
        + "</div>",
        unsafe_allow_html=True,
    )


# ── Tela 1 — Seleção de área ──────────────────────────────────────────────────

def _tela1():
    _step_indicator(1)
    _card_titulo("🎯", "Qual é a sua área de atuação?", "Escolha uma opção — você poderá mudar depois")

    cols = st.columns(3)
    for i, (chave, nome, emoji) in enumerate(AREAS):
        with cols[i % 3]:
            ativo = st.session_state.get("ob_area") == chave
            label = f"{emoji}\n{nome}" + ("\n✓" if ativo else "")
            css   = "area-btn-ativo" if ativo else "area-btn"
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(label, key=f"ob_btn_area_{chave}", use_container_width=True):
                st.session_state.ob_area = chave
                st.session_state.ob_tela = 2
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ── Tela 2 — Edital + data da prova ──────────────────────────────────────────

def _tela2():
    _step_indicator(2)
    _card_titulo("📄", "Você tem o edital disponível?", "O PDF ajuda a criar um plano muito mais preciso")

    tem = st.session_state.get("ob_tem_edital")
    col1, col2 = st.columns(2)
    for chave, col, emoji, titulo, desc in [
        ("sim", col1, "📤", "Sim, tenho o PDF",            "Melhor precisão no plano"),
        ("nao", col2, "📅", "Não tenho / Ainda não lançou","Usaremos um plano base da área"),
    ]:
        with col:
            ativo = (tem is True and chave == "sim") or (tem is False and chave == "nao")
            css   = "ob-card-ativo" if ativo else "ob-card"
            check = "\n✓" if ativo else ""
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(f"{emoji}\n{titulo}\n{desc}{check}", key=f"ob_btn_edital_{chave}", use_container_width=True):
                st.session_state.ob_tem_edital = (chave == "sim")
                if chave == "nao":
                    st.session_state.ob_tela = 3
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if tem is True:
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Selecione o PDF do edital", type=["pdf"], key="ob_pdf")
        if pdf_file:
            st.success(f"✓ {pdf_file.name}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Data prevista da prova** *(opcional)*")
    st.date_input("Data da prova", value=None, min_value=datetime.date.today(),
                  key="ob_data_prova", label_visibility="collapsed")

    col_v, col_n = st.columns(2)
    if col_v.button("← Voltar", key="ob_t2_voltar", use_container_width=True):
        st.session_state.ob_tela = 1
        st.rerun()
    if col_n.button("Continuar →", key="ob_t2_avancar", use_container_width=True, type="primary"):
        st.session_state.ob_tela = 3
        st.rerun()


# ── Tela 3 — Perfil de estudo ─────────────────────────────────────────────────

def _tela3():
    _step_indicator(3)
    _card_titulo("📊", "Você já vem estudando para este concurso?")

    op = st.session_state.get("ob_perfil")
    c1, c2, c3 = st.columns(3)
    for chave, col, emoji, titulo, desc in [
        ("zero",              c1, "🌱", "Estou começando do zero",              "Montaremos o plano completo a partir do início"),
        ("tempo_por_materia", c2, "📚", "Já estudo há algum tempo",              "Informe quanto tempo por matéria e calibramos o nível"),
        ("csv",               c3, "📥", "Tenho histórico em banco de questões",  "Importe seu CSV (TEC, Qconcursos, Gran...) e usamos seus dados reais"),
    ]:
        with col:
            ativo = op == chave
            css   = "perfil-btn-ativo" if ativo else "perfil-btn"
            check = "\n✓ Selecionado" if ativo else ""
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(f"{emoji}\n{titulo}\n{desc}{check}", key=f"ob_btn_perfil_{chave}", use_container_width=True):
                st.session_state.ob_perfil = chave
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if op == "tempo_por_materia":
        area     = st.session_state.get("ob_area", "outro")
        materias = MATERIAS_POR_AREA.get(area, MATERIAS_POR_AREA.get("outro", []))
        st.markdown("<br>**Quanto tempo você já estuda cada matéria?**", unsafe_allow_html=True)
        tempos_sel = st.session_state.get("ob_tempos", {})
        cols_m = st.columns(2)
        for i, mat in enumerate(materias):
            with cols_m[i % 2]:
                slugs = [t[0] for t in TEMPOS]
                idx   = slugs.index(tempos_sel.get(mat, "<1m")) if tempos_sel.get(mat) in slugs else 0
                sel   = st.selectbox(mat, [t[1] for t in TEMPOS], index=idx, key=f"ob_tempo_{mat}")
                tempos_sel[mat] = TEMPOS[[t[1] for t in TEMPOS].index(sel)][0]
        st.session_state.ob_tempos = tempos_sel

    if op == "csv":
        st.markdown(
            "<br>**Importe o CSV exportado do seu banco de questões:**<br>"
            "<span style='font-size:0.82rem;color:#8ab0c8;'>"
            "Formatos aceitos: TEC Concursos, Qconcursos, Gran, Direção</span>",
            unsafe_allow_html=True,
        )
        csv_file = st.file_uploader("Arquivo CSV", type=["csv"], key="ob_csv", label_visibility="collapsed")
        if csv_file:
            st.success(f"Arquivo: {csv_file.name}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_n = st.columns(2)
    if col_v.button("← Voltar", key="ob_t3_voltar", use_container_width=True):
        st.session_state.ob_tela = 2
        st.rerun()
    if col_n.button("Continuar →", key="ob_t3_avancar", use_container_width=True, type="primary"):
        if not op:
            st.warning("Selecione uma opção antes de continuar.")
        else:
            st.session_state.ob_tela = 4
            st.rerun()


# ── Tela 4 — Plataformas ─────────────────────────────────────────────────────

def _tela4():
    _step_indicator(4)
    _card_titulo("🖥️", "Quais plataformas você usa?",
                 "Personaliza suas opções ao lançar baterias de questões")

    selecionadas = set(st.session_state.get("ob_plataformas", PLATAFORMAS_DEFAULT))
    col1, col2   = st.columns(2)
    cols = [col1, col2]

    for i, slug in enumerate(GRUPOS_OPCIONAIS):
        info  = GRUPOS_FONTE[slug]
        ativo = slug in selecionadas
        css   = "plat-btn-ativo" if ativo else "plat-btn"
        with cols[i % 2]:
            st.markdown(f'<div class="{css}"></div>', unsafe_allow_html=True)
            if st.button(f"{info['icon']}\n{info['label']}\n{info['descricao']}",
                         key=f"ob_plat_{slug}", use_container_width=True):
                if ativo:
                    selecionadas.discard(slug)
                else:
                    selecionadas.add(slug)
                st.session_state.ob_plataformas = list(selecionadas)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_n = st.columns(2)
    if col_v.button("← Voltar", key="ob_t4_voltar", use_container_width=True):
        st.session_state.ob_tela = 3
        st.rerun()
    if col_n.button("Continuar →", key="ob_t4_avancar", use_container_width=True, type="primary"):
        st.session_state.ob_plataformas = list(selecionadas)
        st.session_state.ob_tela = 5
        st.rerun()


# ── Tela 5 — Disponibilidade ──────────────────────────────────────────────────

def _tela5():
    _step_indicator(5)
    _card_titulo("⏰", "Qual é a sua disponibilidade?", "Seja realista — o sistema se adapta a você")

    col1, col2 = st.columns(2)
    with col1:
        horas = st.slider("Horas de estudo por dia", 0.5, 12.0,
                          float(st.session_state.get("ob_horas", 3.0)), 0.5,
                          format="%.1f h", key="ob_slider_horas")
        st.session_state.ob_horas = horas
        st.markdown(f'<p style="color:#00b4a6;font-weight:700;font-size:1.1rem;text-align:center;">{horas:.1f}h por dia</p>',
                    unsafe_allow_html=True)
    with col2:
        dias = st.slider("Dias de estudo por semana", 1, 7,
                         int(st.session_state.get("ob_dias", 5)), 1,
                         format="%d dias", key="ob_slider_dias")
        st.session_state.ob_dias = dias
        st.markdown(f'<p style="color:#00b4a6;font-weight:700;font-size:1.1rem;text-align:center;">{dias} dias por semana</p>',
                    unsafe_allow_html=True)

    total_min = horas * dias * 60
    st.markdown(
        f'<div style="background:#19293a;border-radius:10px;padding:16px;text-align:center;margin-top:16px;">'
        f'<p style="color:#8ab0c8;font-size:0.85rem;margin:0 0 4px 0;">Total semanal estimado</p>'
        f'<p style="color:#00b4a6;font-size:1.5rem;font-weight:700;margin:0;">'
        f'{int(total_min // 60)}h {int(total_min % 60)}min / semana</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_n = st.columns(2)
    if col_v.button("← Voltar", key="ob_t5_voltar", use_container_width=True):
        st.session_state.ob_tela = 4
        st.rerun()
    if col_n.button("Gerar meu plano →", key="ob_t5_avancar", use_container_width=True, type="primary"):
        st.session_state.ob_tela = 6
        st.rerun()


# ── Tela 6 — Plano gerado ─────────────────────────────────────────────────────

def _tela6():
    _step_indicator(6)
    _card_titulo("🎉", "Gerando seu plano...", "Aguarde enquanto a IA configura seu cronograma")

    area        = st.session_state.get("ob_area", "outro")
    perfil      = st.session_state.get("ob_perfil", "zero")
    horas       = float(st.session_state.get("ob_horas", 3.0))
    dias        = int(st.session_state.get("ob_dias", 5))
    tem_edital  = bool(st.session_state.get("ob_tem_edital", False))
    data_prova  = st.session_state.get("ob_data_prova")
    plataformas = st.session_state.get("ob_plataformas", PLATAFORMAS_DEFAULT)
    tempos_sel  = st.session_state.get("ob_tempos", {})

    # Monta payload para a API
    payload: dict = {
        "area":          AREA_API.get(area, "Outro"),
        "tem_edital":    tem_edital,
        "perfil":        perfil,
        "horas_por_dia": horas,
        "dias_por_semana": dias,
    }
    if data_prova:
        payload["data_prova"] = str(data_prova)
    if perfil == "tempo_por_materia" and tempos_sel:
        payload["tempo_por_materia"] = tempos_sel

    # Chama a API (somente se ainda não chamou nesta sessão)
    resultado_key = "_ob_resultado"
    if resultado_key not in st.session_state:
        with st.spinner("Criando seu cronograma inteligente..."):
            resultado = api_onboarding(payload)
        st.session_state[resultado_key] = resultado
    else:
        resultado = st.session_state[resultado_key]

    if not resultado:
        st.error("Não foi possível criar o plano. Verifique se o servidor está disponível.")
        if st.button("← Tentar novamente", use_container_width=True):
            st.session_state.pop(resultado_key, None)
            st.rerun()
        return

    # Atualiza session_state do usuário com dados do onboarding
    usuario = st.session_state.get("usuario", {})
    usuario["area_estudo"]  = AREA_API.get(area, "Outro")
    usuario["horas_por_dia"] = horas
    usuario["dias_semana"]  = dias
    usuario["data_prova"]   = str(data_prova) if data_prova else ""
    usuario["plataformas"]  = plataformas
    st.session_state.usuario = usuario
    st.session_state.onboarding_concluido = True
    st.session_state._ob_check_done = True

    # Exibe resultado
    sessoes_geradas = resultado.get("sessoes_geradas", 0)
    st.success(f"Plano criado com sucesso! **{sessoes_geradas} sessões** agendadas.")

    materias = MATERIAS_POR_AREA.get(area, [])
    st.markdown("#### Primeira semana (prévia)")
    carga_dia_min = horas * 60
    for i, mat in enumerate(materias[:dias]):
        st.markdown(
            f'<div style="display:flex;align-items:center;padding:12px 16px;margin-bottom:8px;'
            f'border-radius:10px;background:#19293a;border-left:3px solid #00b4a6;">'
            f'<span style="color:#8ab0c8;font-size:0.8rem;width:52px;flex-shrink:0;">Dia {i+1}</span>'
            f'<span style="color:#e8f4ff;font-weight:600;flex:1;">{mat}</span>'
            f'<span style="color:#8ab0c8;font-size:0.8rem;">Teoria + Exercícios</span>'
            f'<span style="color:#00b4a6;font-weight:700;margin-left:12px;">{int(carga_dia_min)}min</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        f"**Área:** {AREA_LABEL.get(area, area)}  |  "
        f"**Perfil:** {'Iniciante' if perfil=='zero' else 'Com histórico de tempo' if perfil=='tempo_por_materia' else 'Dados reais (CSV)'}  |  "
        f"**Carga:** {horas:.0f}h/dia × {dias} dias"
    )

    if st.button("Ir para o Meu Plano →", key="ob_finalizar", use_container_width=True, type="primary"):
        # Limpa estado do onboarding
        for k in list(st.session_state.keys()):
            if k.startswith("ob_") or k == resultado_key:
                del st.session_state[k]
        st.session_state.pagina = "plano"
        st.rerun()


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    tela = st.session_state.get("ob_tela", 1)

    st.markdown("""<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="stSidebarNav"]     { display: none !important; }
[data-testid="stPopover"]        { display: none !important; }
.block-container { max-width: 900px !important; margin: 0 auto !important;
                   padding-top: 2rem !important; }
.stApp { background: linear-gradient(160deg,#0a1520 0%,#0f1e2a 100%) !important; }

.element-container:has(.area-btn,.ob-card,.perfil-btn,.plat-btn)
    + .element-container [data-testid="stButton"] button,
.element-container:has(.area-btn-ativo,.ob-card-ativo,.perfil-btn-ativo,.plat-btn-ativo)
    + .element-container [data-testid="stButton"] button {
    height: auto !important; border-radius: 16px !important;
    white-space: pre-wrap !important; padding: 20px 16px !important;
    line-height: 1.6 !important; font-size: 0.95rem !important; font-weight: 600 !important;
}
.element-container:has(.area-btn,.ob-card,.perfil-btn)
    + .element-container [data-testid="stButton"] button {
    min-height: 280px !important; border: 1.5px solid #1e4a6a !important;
    background: #19293a !important; color: #e8f4ff !important;
}
.element-container:has(.area-btn-ativo,.ob-card-ativo,.perfil-btn-ativo)
    + .element-container [data-testid="stButton"] button {
    min-height: 280px !important; border: 2px solid #00b4a6 !important;
    background: #0d2535 !important; color: #00b4a6 !important;
}
.element-container:has(.plat-btn) + .element-container [data-testid="stButton"] button {
    min-height: 110px !important; border: 1.5px solid #1e4a6a !important;
    background: #162535 !important; color: #e8f4ff !important;
}
.element-container:has(.plat-btn-ativo) + .element-container [data-testid="stButton"] button {
    min-height: 110px !important; border: 2px solid #00b4a6 !important;
    background: #0d2535 !important; color: #00b4a6 !important;
}
</style>""", unsafe_allow_html=True)

    components.html("""<script>
(function() {
    var NAV = ['Voltar','Continuar','Dashboard','Gerar','Entrar','Sair','Resetar','Meu Plano','Plano','Tentar'];
    var DONE = new WeakSet();
    function buildCard(btn) {
        if (DONE.has(btn)) return;
        var txt = (btn.innerText || '').trim();
        if (!txt) return;
        if (NAV.some(function(n){ return txt.includes(n); })) return;
        var lines = txt.split('\\n').map(function(l){ return l.trim(); }).filter(Boolean);
        if (lines.length < 2) return;
        var emoji = lines[0], titulo = lines[1];
        var desc  = lines.slice(2).join(' ').replace(/\u2713.*/, '').trim();
        var ativo = txt.indexOf('\u2713') !== -1;
        var isCompact = desc.length < 50;
        if (isCompact) {
            btn.innerHTML = '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;padding:14px 12px;gap:6px;">'
                + '<div style="font-size:2rem;line-height:1;">' + emoji + '</div>'
                + '<div style="font-size:0.9rem;font-weight:700;text-align:center;">' + titulo + '</div>'
                + (desc ? '<div style="font-size:0.74rem;text-align:center;opacity:0.65;line-height:1.35;">' + desc + '</div>' : '')
                + (ativo ? '<div style="font-size:0.7rem;font-weight:800;color:#00b4a6;margin-top:2px;">✓ Ativo</div>' : '')
                + '</div>';
        } else {
            btn.innerHTML = '<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-start;height:100%;padding:28px 16px 24px;">'
                + '<div style="font-size:3.4rem;line-height:1;margin-bottom:28px;">' + emoji + '</div>'
                + '<div style="font-size:1.05rem;font-weight:700;text-align:center;margin-bottom:10px;">' + titulo + '</div>'
                + (desc ? '<div style="font-size:0.82rem;text-align:center;opacity:0.6;line-height:1.45;">' + desc + '</div>' : '')
                + '</div>';
        }
        Object.assign(btn.style, {
            minHeight: isCompact ? 'auto' : '280px', height: 'auto',
            borderRadius: isCompact ? '14px' : '20px', padding: '0',
            whiteSpace: 'normal', lineHeight: '1',
            background: ativo ? '#0d2535' : (isCompact ? '#162535' : '#19293a'),
            color:      ativo ? '#00b4a6' : (isCompact ? '#d0e4f0' : '#e8f4ff'),
            border:     ativo ? '2px solid #00b4a6' : ('1.5px solid ' + (isCompact ? '#1e3a5c' : '#1e4a6a'))
        });
        DONE.add(btn);
    }
    function apply() {
        try { parent.document.querySelectorAll('[data-testid="stButton"] button').forEach(buildCard); } catch(e) {}
    }
    apply();
    try { new MutationObserver(apply).observe(parent.document.body, {childList:true, subtree:true}); } catch(e) {}
})();
</script>""", height=0)

    st.markdown('<div style="padding:0 0 32px 0;">', unsafe_allow_html=True)

    if tela == 1:   _tela1()
    elif tela == 2: _tela2()
    elif tela == 3: _tela3()
    elif tela == 4: _tela4()
    elif tela == 5: _tela5()
    elif tela == 6: _tela6()

    st.markdown("</div>", unsafe_allow_html=True)
