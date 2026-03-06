"""
pg_registrar_erros.py
Tela para registrar erros de uma bateria recem-finalizada.
Acessada automaticamente apos "Finalizar Bateria".
"""

import streamlit as st
from datetime import datetime
from database import inserir_erro


def render():
    id_bateria = st.session_state.get("id_bateria_erros", "")
    materia    = st.session_state.get("mats_bateria_erros", "")

    st.title(f"Registrar Erros — {id_bateria}")
    st.caption(f"Disciplina(s): {materia}")

    # Inicializa a lista de topicos registrados nesta sessao
    if "erros_registrados" not in st.session_state:
        st.session_state.erros_registrados = []

    registrados = st.session_state.erros_registrados
    if registrados:
        st.success(
            f"{len(registrados)} topico(s) registrado(s): "
            + ", ".join(registrados)
        )

    st.divider()
    st.subheader("Novo Erro")

    # Contador para resetar o formulario apos cada adicao
    if "erro_form_cnt" not in st.session_state:
        st.session_state.erro_form_cnt = 0
    fc = st.session_state.erro_form_cnt

    # Materia do erro: preenchida automaticamente se a bateria tiver so 1 materia
    mat_default = materia if "," not in materia else ""
    mat_err = st.text_input(
        "Materia do Erro",
        value=mat_default,
        placeholder=materia,
        key=f"e_mat_{fc}",
    )
    topico = st.text_input(
        "Topico do Erro",
        placeholder="Ex: Processo Administrativo — Fases",
        key=f"e_top_{fc}",
    )
    qtd = st.number_input(
        "Quantidade de Erros", min_value=1, value=1, step=1, key=f"e_qtd_{fc}"
    )
    obs  = st.text_input(
        "Observacao",
        placeholder="Ex: Confundiu prazo recursal com prazo de ato",
        key=f"e_obs_{fc}",
    )
    prov = st.text_input(
        "Providencia",
        placeholder="Ex: Revisar flashcard / refazer questoes CEI",
        key=f"e_prov_{fc}",
    )

    # ── Botoes ────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 2])

    def _salvar():
        """Valida e salva o erro atual no banco."""
        if not mat_err.strip():
            st.error("Materia do erro e obrigatoria.")
            return False
        if not topico.strip():
            st.error("Topico do erro e obrigatorio.")
            return False
        inserir_erro({
            "id_bateria":  id_bateria,
            "materia":     mat_err.strip(),
            "topico":      topico.strip(),
            "qtd_erros":   int(qtd),
            "data":        datetime.now().strftime("%d/%m/%Y"),
            "observacao":  obs.strip(),
            "providencia": prov.strip(),
        })
        return True

    if col1.button("+ Adicionar Outro Topico", use_container_width=True):
        if _salvar():
            st.session_state.erros_registrados.append(topico.strip())
            st.session_state.erro_form_cnt += 1  # reseta o formulario
            st.rerun()

    if col2.button("Salvar e Finalizar", type="primary", use_container_width=True):
        if _salvar():
            _limpar_e_ir_dashboard()

    if col3.button("Finalizar sem mais erros", use_container_width=True):
        _limpar_e_ir_dashboard()


def _limpar_e_ir_dashboard():
    """Limpa o estado do fluxo de erros e volta ao dashboard."""
    for k in ["erros_registrados", "id_bateria_erros",
              "mats_bateria_erros", "erro_form_cnt"]:
        st.session_state.pop(k, None)
    st.session_state.pagina = "dashboard"
    st.rerun()
