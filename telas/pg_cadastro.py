"""
pg_cadastro.py
Tela de CRUD para materias e seus assuntos.
Materias cadastradas aqui aparecem nos dropdowns de "Lancar Bateria".
"""

import streamlit as st
from database import (
    get_materias, get_assuntos,
    inserir_materia, inserir_assunto,
    remover_assunto, remover_materia,
)


def render():
    st.title("Cadastro de Materias e Assuntos")

    col_left, col_right = st.columns(2)

    # ── Painel esquerdo: Materias ─────────────────────────────────────────────
    with col_left:
        st.subheader("Materias")

        # Formulario para adicionar nova materia
        with st.form("form_add_mat", clear_on_submit=True):
            nova_mat = st.text_input(
                "Nova materia", placeholder="Ex: Direito Constitucional"
            )
            if st.form_submit_button("+ Adicionar Materia", use_container_width=True):
                nova_mat = nova_mat.strip()
                if not nova_mat:
                    st.error("Informe o nome da materia.")
                elif nova_mat in get_materias(st.session_state.usuario["id"]):
                    st.warning(f"A materia '{nova_mat}' ja existe.")
                else:
                    inserir_materia(nova_mat, st.session_state.usuario["id"])
                    # Seleciona automaticamente a materia recem-criada
                    st.session_state.mat_selecionada = nova_mat
                    st.rerun()

        st.divider()

        # Lista de materias com botao de selecionar e de excluir
        materias = get_materias(st.session_state.usuario["id"])
        if not materias:
            st.info("Nenhuma materia cadastrada.")
        else:
            mat_ativa = st.session_state.get("mat_selecionada")
            for mat in materias:
                c1, c2 = st.columns([5, 1])
                is_sel = (mat == mat_ativa)
                if c1.button(
                    mat,
                    key=f"sel_{mat}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                ):
                    st.session_state.mat_selecionada = mat
                    st.rerun()
                if c2.button("✕", key=f"del_mat_{mat}", help=f"Remover {mat}"):
                    remover_materia(mat, st.session_state.usuario["id"])
                    if st.session_state.get("mat_selecionada") == mat:
                        st.session_state.pop("mat_selecionada", None)
                    st.rerun()

    # ── Painel direito: Assuntos ──────────────────────────────────────────────
    with col_right:
        st.subheader("Assuntos")

        mat_ativa = st.session_state.get("mat_selecionada")
        if not mat_ativa:
            st.info("Selecione uma materia ao lado para gerenciar seus assuntos.")
        else:
            st.caption(f"Materia selecionada: **{mat_ativa}**")

            # Formulario para adicionar novo assunto
            with st.form("form_add_ass", clear_on_submit=True):
                novo_ass = st.text_input(
                    "Novo assunto", placeholder="Ex: Atos Administrativos"
                )
                if st.form_submit_button("+ Adicionar Assunto", use_container_width=True):
                    novo_ass = novo_ass.strip()
                    if not novo_ass:
                        st.error("Informe o nome do assunto.")
                    elif novo_ass in get_assuntos(mat_ativa, st.session_state.usuario["id"]):
                        st.warning(f"O assunto '{novo_ass}' ja existe para esta materia.")
                    else:
                        inserir_assunto(mat_ativa, novo_ass, st.session_state.usuario["id"])
                        st.rerun()

            st.divider()

            # Lista de assuntos com botao de excluir
            assuntos = get_assuntos(mat_ativa, st.session_state.usuario["id"])
            if not assuntos:
                st.info("Nenhum assunto cadastrado para esta materia.")
            else:
                for ass in assuntos:
                    c1, c2 = st.columns([5, 1])
                    c1.write(ass)
                    if c2.button("✕", key=f"del_ass_{mat_ativa}_{ass}", help=f"Remover '{ass}'"):
                        remover_assunto(mat_ativa, ass, st.session_state.usuario["id"])
                        st.rerun()
