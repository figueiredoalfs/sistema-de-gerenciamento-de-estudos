"""
telas/pg_plano.py
Exibe o plano de estudos gerado no onboarding.
"""

import streamlit as st
from database import get_perfil

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

AREAS_LABEL = {
    "fiscal": "Fiscal", "juridica": "Jurídica", "policial": "Policial",
    "ti": "TI", "saude": "Saúde", "outro": "Outro",
}

PERFIL_LABEL = {
    "zero": "Iniciante", "tempo_por_materia": "Estudante", "csv": "Com histórico",
}

TIPOS_SESSAO = ["Teoria", "Exercícios", "Flashcards", "Vídeo", "Revisão"]


def render():
    usuario_id = st.session_state.usuario["id"]
    perfil = get_perfil(usuario_id)

    area    = perfil.get("area_estudo", "")
    horas   = float(perfil.get("horas_dia") or 3.0)
    dias    = int(perfil.get("dias_semana") or 5)
    tipo_p  = perfil.get("perfil_estudo", "zero")
    data_p  = perfil.get("data_prova", "")

    # Sem plano configurado
    if not area or perfil.get("plano") != "ativo":
        st.markdown("## Meu Plano")
        st.info("Você ainda não configurou seu plano de estudos.")
        if st.button("Configurar plano agora →", type="primary"):
            st.session_state.ob_tela = 1
            st.session_state.pagina  = "onboarding"
            st.rerun()
        return

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    st.markdown("## Meu Plano de Estudos")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Área", AREAS_LABEL.get(area, area))
    col2.metric("Perfil", PERFIL_LABEL.get(tipo_p, tipo_p))
    col3.metric("Carga diária", f"{horas:.0f}h/dia × {dias} dias")
    col4.metric("Total semanal", f"{int(horas * dias)}h/semana")

    if data_p:
        st.markdown(
            f'<p style="color:#8ab0c8;font-size:0.85rem;margin-top:-8px;">📅 Data da prova: <strong>{data_p}</strong></p>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Semana de estudos ──────────────────────────────────────────────────────
    st.markdown("#### Primeira semana")

    materias = MATERIAS_POR_AREA.get(area, MATERIAS_POR_AREA["outro"])
    carga_dia_min = int(horas * 60)

    cores_tipo = {
        "Teoria":     "#1a6b5a",
        "Exercícios": "#1a4b6a",
        "Flashcards": "#5a2d6a",
        "Vídeo":      "#6a3d1a",
        "Revisão":    "#4a4a1a",
    }

    for i in range(dias):
        mat = materias[i % len(materias)]
        tipo = TIPOS_SESSAO[i % len(TIPOS_SESSAO)]
        cor = cores_tipo[tipo]
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:14px 18px;'
            f'margin-bottom:8px;border-radius:10px;background:#19293a;border-left:4px solid #00b4a6;">'
            f'<span style="color:#8ab0c8;font-size:0.82rem;min-width:50px;">Dia {i+1}</span>'
            f'<span style="color:#e8f4ff;font-weight:600;flex:1;">{mat}</span>'
            f'<span style="background:{cor};color:#fff;font-size:0.75rem;padding:3px 10px;'
            f'border-radius:20px;font-weight:600;">{tipo}</span>'
            f'<span style="color:#00b4a6;font-weight:700;min-width:60px;text-align:right;">'
            f'{carga_dia_min}min</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Matérias do plano ──────────────────────────────────────────────────────
    st.markdown("#### Matérias do plano")
    cols = st.columns(3)
    for i, mat in enumerate(materias):
        with cols[i % 3]:
            st.markdown(
                f'<div style="padding:12px 14px;border-radius:8px;background:#19293a;'
                f'border-left:3px solid #00b4a6;margin-bottom:8px;">'
                f'<p style="color:#e8f4ff;font-weight:600;margin:0;font-size:0.88rem;">{mat}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    if st.button("Refazer onboarding", key="btn_refazer_plano"):
        for k in list(st.session_state.keys()):
            if k.startswith("ob_") or k == "onboarding_concluido":
                del st.session_state[k]
        st.session_state.ob_tela = 1
        st.session_state.pagina  = "onboarding"
        st.rerun()
