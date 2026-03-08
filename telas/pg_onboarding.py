"""
telas/pg_onboarding.py
Fluxo de onboarding do AprovAI — 5 telas, < 3 minutos.

Tela 1: seleção de área (1 clique)
Tela 2: edital disponível? + upload PDF + data da prova
Tela 3: já vem estudando? → 3 perfis (A/B/C)
Tela 4: horas/dia + dias/semana
Tela 5: cronograma gerado — aluno vê valor imediato
"""

import io
import json
import datetime
import streamlit as st
import streamlit.components.v1 as components
from database import salvar_perfil

# ── Constantes ────────────────────────────────────────────────────────────────

AREAS = [
    ("fiscal",    "Fiscal",    "🏛️"),
    ("juridica",  "Jurídica",  "⚖️"),
    ("policial",  "Policial",  "🚔"),
    ("ti",        "TI",        "💻"),
    ("saude",     "Saúde",     "🏥"),
    ("outro",     "Outro",     "📋"),
]

MATERIAS_POR_AREA = {
    "fiscal":   ["Direito Tributário", "Contabilidade", "Direito Administrativo",
                 "Língua Portuguesa", "Raciocínio Lógico", "Legislação Específica"],
    "juridica": ["Direito Constitucional", "Direito Civil", "Direito Penal",
                 "Direito Administrativo", "Língua Portuguesa", "Direito Processual Civil"],
    "policial": ["Direito Penal", "Direito Processual Penal", "Direito Constitucional",
                 "Língua Portuguesa", "Raciocínio Lógico", "Conhecimentos Gerais"],
    "ti":       ["Algoritmos e Estruturas de Dados", "Banco de Dados", "Redes de Computadores",
                 "Segurança da Informação", "Engenharia de Software", "Língua Portuguesa"],
    "saude":    ["Conhecimentos Específicos", "Legislação SUS", "Ética Profissional",
                 "Língua Portuguesa", "Raciocínio Lógico", "Atualidades"],
    "outro":    ["Língua Portuguesa", "Raciocínio Lógico", "Conhecimentos Gerais",
                 "Direito Administrativo", "Informática", "Atualidades"],
}

TEMPOS = [
    ("<1m",  "Menos de 1 mês",  1),
    ("1-3m", "1 a 3 meses",     2),
    ("3-6m", "3 a 6 meses",     3),
    (">6m",  "Mais de 6 meses", 4),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _step_indicator(atual: int, total: int = 5):
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
    st.markdown(
        f'<div style="text-align:center;margin-bottom:24px;">{pontos}</div>',
        unsafe_allow_html=True,
    )


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
            css_class = "area-btn-ativo" if ativo else "area-btn"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"ob_btn_area_{chave}", use_container_width=True):
                st.session_state.ob_area = chave
                st.session_state.ob_tela = 2
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ── Tela 2 — Edital + data da prova ──────────────────────────────────────────

def _tela2():
    _step_indicator(2)
    _card_titulo("📄", "Você tem o edital disponível?", "O PDF ajuda a criar um plano muito mais preciso")

    tem = st.session_state.get("ob_tem_edital")  # True / False / None

    col1, col2 = st.columns(2)
    opcoes = [
        ("sim",  col1, "📤", "Sim, tenho o PDF",              "Melhor precisão no plano"),
        ("nao",  col2, "📅", "Não tenho / Ainda não lançou",  "Usaremos um plano base da área"),
    ]
    for chave, col, emoji, titulo, desc in opcoes:
        with col:
            ativo = (tem is True and chave == "sim") or (tem is False and chave == "nao")
            css_class = "ob-card-ativo" if ativo else "ob-card"
            check = "\n✓" if ativo else ""
            label = f"{emoji}\n{titulo}\n{desc}{check}"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"ob_btn_edital_{chave}", use_container_width=True):
                st.session_state.ob_tem_edital = (chave == "sim")
                if chave == "nao":
                    st.session_state.ob_tela = 3
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Upload aparece abaixo do card "Sim" quando selecionado
    if tem is True:
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_file = st.file_uploader(
            "Selecione o PDF do edital",
            type=["pdf"],
            key="ob_pdf",
        )
        if pdf_file:
            st.success(f"✓ {pdf_file.name}")
            st.session_state.ob_pdf_nome = pdf_file.name

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Data prevista da prova** *(opcional)*")
    st.date_input(
        "Data da prova",
        value=None,
        min_value=datetime.date.today(),
        key="ob_data_prova",
        label_visibility="collapsed",
    )

    col_v, col_n = st.columns([1, 1])
    with col_v:
        if st.button("← Voltar", key="ob_t2_voltar", use_container_width=True):
            st.session_state.ob_tela = 1
            st.rerun()
    with col_n:
        if st.button("Continuar →", key="ob_t2_avancar", use_container_width=True, type="primary"):
            st.session_state.ob_tela = 3
            st.rerun()


# ── Tela 3 — Perfil de estudo ─────────────────────────────────────────────────

def _tela3():
    _step_indicator(3)
    _card_titulo("📊", "Você já vem estudando para este concurso?")

    op = st.session_state.get("ob_perfil")

    c1, c2, c3 = st.columns(3)
    perfis = [
        ("zero",              c1, "🌱", "Estou começando do zero",       "Montaremos o plano completo a partir do início"),
        ("tempo_por_materia", c2, "📚", "Já estudo há algum tempo",       "Informe quanto tempo por matéria e calibramos o nível"),
        ("csv",               c3, "📥", "Tenho histórico no Qconcursos",  "Importe seu CSV e usamos seus dados reais"),
    ]

    for chave, col, emoji, titulo, desc in perfis:
        with col:
            ativo = op == chave
            css_class = "perfil-btn-ativo" if ativo else "perfil-btn"
            check = "\n✓ Selecionado" if ativo else ""
            label = f"{emoji}\n{titulo}\n{desc}{check}"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"ob_btn_perfil_{chave}", use_container_width=True):
                st.session_state.ob_perfil = chave
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Perfil B — tempo por matéria
    if op == "tempo_por_materia":
        area = st.session_state.get("ob_area", "outro")
        materias = MATERIAS_POR_AREA.get(area, MATERIAS_POR_AREA["outro"])
        st.markdown("<br>**Quanto tempo você já estuda cada matéria?**", unsafe_allow_html=True)
        tempos_sel = st.session_state.get("ob_tempos", {})
        cols_m = st.columns(2)
        for i, mat in enumerate(materias):
            with cols_m[i % 2]:
                idx = [t[0] for t in TEMPOS].index(tempos_sel.get(mat, "<1m")) if tempos_sel.get(mat) in [t[0] for t in TEMPOS] else 0
                sel = st.selectbox(
                    mat,
                    options=[t[1] for t in TEMPOS],
                    index=idx,
                    key=f"ob_tempo_{mat}",
                )
                tempos_sel[mat] = TEMPOS[[t[1] for t in TEMPOS].index(sel)][0]
        st.session_state.ob_tempos = tempos_sel

    # Perfil C — CSV
    if op == "csv":
        st.markdown("<br>**Importe o CSV exportado do Qconcursos ou TEC Concursos:**", unsafe_allow_html=True)
        csv_file = st.file_uploader("Arquivo CSV", type=["csv"], key="ob_csv", label_visibility="collapsed")
        if csv_file:
            st.success(f"Arquivo: {csv_file.name}")
            st.session_state.ob_csv_nome = csv_file.name

    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_n = st.columns([1, 1])
    with col_v:
        if st.button("← Voltar", key="ob_t3_voltar", use_container_width=True):
            st.session_state.ob_tela = 2
            st.rerun()
    with col_n:
        if st.button("Continuar →", key="ob_t3_avancar", use_container_width=True, type="primary"):
            if not op:
                st.warning("Selecione uma opção antes de continuar.")
            else:
                st.session_state.ob_tela = 4
                st.rerun()


# ── Tela 4 — Disponibilidade ──────────────────────────────────────────────────

def _tela4():
    _step_indicator(4)
    _card_titulo("⏰", "Qual é a sua disponibilidade?", "Seja realista — o sistema se adapta a você")

    col1, col2 = st.columns(2)
    with col1:
        horas = st.slider(
            "Horas de estudo por dia",
            min_value=0.5, max_value=12.0,
            value=float(st.session_state.get("ob_horas", 3.0)),
            step=0.5,
            format="%.1f h",
            key="ob_slider_horas",
        )
        st.session_state.ob_horas = horas
        st.markdown(
            f'<p style="color:#00b4a6;font-weight:700;font-size:1.1rem;text-align:center;">'
            f'{horas:.1f}h por dia</p>',
            unsafe_allow_html=True,
        )

    with col2:
        dias = st.slider(
            "Dias de estudo por semana",
            min_value=1, max_value=7,
            value=int(st.session_state.get("ob_dias", 5)),
            step=1,
            format="%d dias",
            key="ob_slider_dias",
        )
        st.session_state.ob_dias = dias
        st.markdown(
            f'<p style="color:#00b4a6;font-weight:700;font-size:1.1rem;text-align:center;">'
            f'{dias} dias por semana</p>',
            unsafe_allow_html=True,
        )

    total_min = horas * dias * 60
    st.markdown(
        f'<div style="background:#19293a;border-radius:10px;padding:16px;text-align:center;margin-top:16px;">'
        f'<p style="color:#8ab0c8;font-size:0.85rem;margin:0 0 4px 0;">Total semanal estimado</p>'
        f'<p style="color:#00b4a6;font-size:1.5rem;font-weight:700;margin:0;">'
        f'{int(total_min // 60)}h {int(total_min % 60)}min / semana</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_n = st.columns([1, 1])
    with col_v:
        if st.button("← Voltar", key="ob_t4_voltar", use_container_width=True):
            st.session_state.ob_tela = 3
            st.rerun()
    with col_n:
        if st.button("Gerar meu plano →", key="ob_t4_avancar", use_container_width=True, type="primary"):
            st.session_state.ob_tela = 5
            st.rerun()


# ── Tela 5 — Cronograma gerado ────────────────────────────────────────────────

def _tela5():
    _step_indicator(5)
    _card_titulo("🎉", "Seu plano está pronto!", "Aqui está a sua primeira semana de estudos")

    area    = st.session_state.get("ob_area", "outro")
    perfil  = st.session_state.get("ob_perfil", "zero")
    horas   = float(st.session_state.get("ob_horas", 3.0))
    dias    = int(st.session_state.get("ob_dias", 5))
    materias = MATERIAS_POR_AREA.get(area, MATERIAS_POR_AREA["outro"])

    # Salva todos os dados do onboarding no perfil do usuario
    usuario_id = st.session_state.usuario["id"]
    salvar_perfil(usuario_id, {
        "plano":          "ativo",
        "area_estudo":    area,
        "horas_dia":      horas,
        "dias_semana":    dias,
        "perfil_estudo":  perfil,
        "data_prova":     str(st.session_state.get("ob_data_prova", "")),
    })
    st.session_state.ob_concluido = True

    # Gera preview da semana (simulado visual — sem backend real ainda)
    carga_dia_min = horas * 60
    sessoes_preview = []
    for i, mat in enumerate(materias[:dias]):
        sessoes_preview.append({
            "dia": f"Dia {i+1}",
            "materia": mat,
            "tipo": "Teoria + Exercícios",
            "duracao": f"{int(carga_dia_min)}min",
        })

    st.markdown("#### Primeira semana")
    for s in sessoes_preview:
        st.markdown(
            f'<div style="display:flex;align-items:center;padding:12px 16px;margin-bottom:8px;'
            f'border-radius:10px;background:#19293a;border-left:3px solid #00b4a6;">'
            f'<span style="color:#8ab0c8;font-size:0.8rem;width:52px;flex-shrink:0;">{s["dia"]}</span>'
            f'<span style="color:#e8f4ff;font-weight:600;flex:1;">{s["materia"]}</span>'
            f'<span style="color:#8ab0c8;font-size:0.8rem;">{s["tipo"]}</span>'
            f'<span style="color:#00b4a6;font-weight:700;margin-left:12px;">{s["duracao"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        f"**Área:** {dict([(k,v) for k,v,_ in AREAS]).get(area, area)}  |  "
        f"**Perfil:** {'Iniciante' if perfil=='zero' else 'Estudante' if perfil=='tempo_por_materia' else 'Com histórico'}  |  "
        f"**Carga:** {horas:.0f}h/dia × {dias} dias"
    )

    if st.button("Ir para o Dashboard →", key="ob_finalizar", use_container_width=True, type="primary"):
        # Limpa estado do onboarding
        for k in list(st.session_state.keys()):
            if k.startswith("ob_"):
                del st.session_state[k]
        st.session_state.onboarding_concluido = True
        st.session_state.pagina = "dashboard"
        st.rerun()


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    tela = st.session_state.get("ob_tela", 1)

    # Full-screen: oculta sidebar, perfil e expande layout
    st.markdown("""
    <style>
    [data-testid="stSidebar"]          { display: none !important; }
    [data-testid="stSidebarNav"]       { display: none !important; }
    [data-testid="stPopover"]          { display: none !important; }
    .block-container                   { max-width: 900px !important; margin: 0 auto !important;
                                         padding-top: 2rem !important; }
    .stApp                             { background: linear-gradient(160deg,#0a1520 0%,#0f1e2a 100%) !important; }

    /* :has() para Chrome 105+ */
    .element-container:has(.area-btn,.ob-card,.perfil-btn)
        + .element-container [data-testid="stButton"] button,
    .element-container:has(.area-btn-ativo,.ob-card-ativo,.perfil-btn-ativo)
        + .element-container [data-testid="stButton"] button {
        min-height: 360px !important; height: auto !important;
        border-radius: 20px !important; white-space: pre-wrap !important;
        padding: 32px 20px !important; line-height: 1.8 !important;
        font-size: 1rem !important; font-weight: 600 !important;
    }
    .element-container:has(.area-btn,.ob-card,.perfil-btn)
        + .element-container [data-testid="stButton"] button {
        border: 1.5px solid #1e4a6a !important;
        background: #19293a !important; color: #e8f4ff !important;
    }
    .element-container:has(.area-btn-ativo,.ob-card-ativo,.perfil-btn-ativo)
        + .element-container [data-testid="stButton"] button {
        border: 2px solid #00b4a6 !important;
        background: #0d2535 !important; color: #00b4a6 !important;
    }

    /* Botoes de navegacao (Voltar / Continuar) — altura normal */
    .element-container:has(.area-btn,.ob-card,.perfil-btn) ~ * [data-testid="stButton"] button,
    .element-container:has(.area-btn-ativo,.ob-card-ativo,.perfil-btn-ativo) ~ * [data-testid="stButton"] button {
        min-height: unset !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # JS via components.html — única forma garantida de executar JS no Streamlit
    # parent.document acessa o DOM principal (mesma origem em localhost)
    components.html("""
    <script>
    (function() {
        var NAV = ['Voltar','Continuar','Dashboard','Gerar','Entrar','Sair','Resetar','Meu Perfil'];
        var DONE = new WeakSet();

        function buildCard(btn) {
            if (DONE.has(btn)) return;
            var txt = (btn.innerText || btn.textContent || '').trim();
            if (!txt) return;
            if (NAV.some(function(n){ return txt.includes(n); })) return;
            var lines = txt.split('\\n').map(function(l){ return l.trim(); }).filter(Boolean);
            if (lines.length < 2) return;

            var emoji  = lines[0];
            var titulo = lines[1];
            var desc   = lines.slice(2).join(' ').replace(/\u2713.*/, '').trim();
            var ativo  = txt.indexOf('\u2713') !== -1;

            btn.innerHTML =
                '<div style="display:flex;flex-direction:column;align-items:center;' +
                'justify-content:flex-start;height:100%;padding:28px 16px 24px;">' +
                  '<div style="font-size:3.4rem;line-height:1;margin-bottom:28px;">' + emoji + '</div>' +
                  '<div style="font-size:1.05rem;font-weight:700;text-align:center;margin-bottom:10px;">' + titulo + '</div>' +
                  (desc ? '<div style="font-size:0.82rem;text-align:center;opacity:0.6;line-height:1.45;">' + desc + '</div>' : '') +
                '</div>';

            Object.assign(btn.style, {
                minHeight: '320px', height: 'auto',
                borderRadius: '20px', padding: '0',
                whiteSpace: 'normal', lineHeight: '1',
                background: ativo ? '#0d2535' : '#19293a',
                color:      ativo ? '#00b4a6' : '#e8f4ff',
                border:     ativo ? '2px solid #00b4a6' : '1.5px solid #1e4a6a'
            });
            DONE.add(btn);
        }

        function apply() {
            try {
                parent.document.querySelectorAll('[data-testid="stButton"] button')
                    .forEach(buildCard);
            } catch(e) {}
        }

        apply();
        try {
            new MutationObserver(apply)
                .observe(parent.document.body, {childList:true, subtree:true});
        } catch(e) {}
    })();
    </script>
    """, height=0)

    st.markdown(
        '<div style="padding:0 0 32px 0;">',
        unsafe_allow_html=True,
    )

    if tela == 1:
        _tela1()
    elif tela == 2:
        _tela2()
    elif tela == 3:
        _tela3()
    elif tela == 4:
        _tela4()
    elif tela == 5:
        _tela5()

    st.markdown("</div>", unsafe_allow_html=True)
