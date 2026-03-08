"""
pg_lancar_bateria.py
Tela para lancar uma nova bateria de questoes.

Opcao B: os itens ficam acumulados em st.session_state e so sao gravados
no banco ao clicar em "Finalizar Bateria" — sem registros intermediarios.
"""

import streamlit as st
from datetime import datetime
from database import gerar_proximo_id, inserir_lancamentos, get_materias, get_assuntos


def _inicializar_estado():
    """Inicializa as variaveis de estado da bateria em andamento."""
    if "bat_id" not in st.session_state:
        st.session_state.bat_id      = gerar_proximo_id(st.session_state.usuario["id"])
        st.session_state.bat_data    = datetime.now().strftime("%d/%m/%Y")
        st.session_state.bat_fonte   = ""
        st.session_state.bat_itens   = []   # lista de dicts por materia
        st.session_state.form_cnt    = 0    # contador para resetar o formulario


def render():
    _inicializar_estado()

    st.title("Lancar Nova Bateria")
    st.caption("Adicione quantas materias/disciplinas quiser antes de finalizar.")

    # ── Identificacao da bateria ───────────────────────────────────────────────
    with st.expander("Identificacao da Bateria", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.text_input("ID da Bateria", value=st.session_state.bat_id,
                      disabled=True)
        st.session_state.bat_data  = c2.text_input(
            "Data", value=st.session_state.bat_data, key="bat_data_input")
        st.session_state.bat_fonte = c3.text_input(
            "Fonte principal", value=st.session_state.bat_fonte,
            placeholder="GURUJA / GEMINI / TEC / ...", key="bat_fonte_input")

    # ── Lista de materias adicionadas ─────────────────────────────────────────
    st.subheader("Materias nesta Bateria")
    itens = st.session_state.bat_itens

    if itens:
        tot_q  = sum(i["total"]   for i in itens)
        tot_a  = sum(i["acertos"] for i in itens)
        perc_g = f"{tot_a/tot_q*100:.1f}%" if tot_q > 0 else "—"
        st.caption(
            f"{len(itens)} materia(s)  |  {tot_q} questoes  |  "
            f"{tot_a} acertos  ({perc_g})"
        )
        preview = [
            {
                "Materia":   i["materia"],
                "Subtopico": i["subtopico"],
                "Acertos":   i["acertos"],
                "Total":     i["total"],
                "%":         f"{i['acertos']/i['total']*100:.1f}%" if i["total"] > 0 else "—",
            }
            for i in itens
        ]
        st.dataframe(preview, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma materia adicionada ainda.")

    st.divider()

    # ── Formulario para adicionar uma materia ─────────────────────────────────
    # O sufixo form_cnt no key forca o reset dos widgets apos cada adicao
    st.subheader("Adicionar Materia / Disciplina")
    fc = st.session_state.form_cnt

    materias_cad = get_materias(st.session_state.usuario["id"])
    col_m, col_a, col_t, col_s = st.columns([2, 1, 1, 2])

    mat_sel = col_m.selectbox(
        "Materia / Disciplina",
        options=[""] + materias_cad,
        key=f"form_mat_{fc}",
    )
    acertos = col_a.number_input(
        "Acertos", min_value=0, value=0, step=1, key=f"form_ace_{fc}"
    )
    total = col_t.number_input(
        "Total", min_value=1, value=10, step=1, key=f"form_tot_{fc}"
    )

    assuntos_cad = get_assuntos(mat_sel, st.session_state.usuario["id"]) if mat_sel else []
    sub_sel = col_s.selectbox(
        "Subtopico / Assunto",
        options=[""] + assuntos_cad,
        key=f"form_sub_{fc}",
    )

    # ── Botoes de acao ────────────────────────────────────────────────────────
    col_b1, col_b2, col_b3 = st.columns([2, 2, 2])

    if col_b1.button("+ Adicionar Materia", use_container_width=True):
        mat = mat_sel.strip()
        if not mat:
            st.error("Selecione ou informe a Materia / Disciplina.")
        elif acertos > total:
            st.error(f"Acertos ({acertos}) nao pode ser maior que Total ({total}).")
        else:
            st.session_state.bat_itens.append({
                "materia":   mat,
                "subtopico": sub_sel.strip(),
                "acertos":   int(acertos),
                "total":     int(total),
            })
            st.session_state.form_cnt += 1  # reseta o formulario
            st.rerun()

    if col_b2.button("Finalizar Bateria", type="primary", use_container_width=True):
        if not st.session_state.bat_itens:
            st.warning("Adicione pelo menos uma materia antes de finalizar.")
        else:
            id_b  = st.session_state.bat_id
            data  = st.session_state.bat_data
            fonte = st.session_state.bat_fonte

            # Monta a lista de registros e grava tudo de uma vez
            registros = []
            for item in st.session_state.bat_itens:
                perc = round(item["acertos"] / item["total"] * 100, 1) if item["total"] > 0 else 0.0
                registros.append({
                    "id_bateria": id_b,
                    "materia":    item["materia"],
                    "data":       data,
                    "acertos":    item["acertos"],
                    "total":      item["total"],
                    "fonte":      fonte,
                    "subtopico":  item["subtopico"],
                    "percentual": perc,
                })
            inserir_lancamentos(registros, st.session_state.usuario["id"])

            mats = ", ".join(dict.fromkeys(i["materia"] for i in st.session_state.bat_itens))

            # Limpa o estado da bateria atual
            for k in ["bat_id", "bat_data", "bat_fonte", "bat_itens",
                      "form_cnt", "bat_data_input", "bat_fonte_input"]:
                st.session_state.pop(k, None)

            # Passa os dados para a tela de registrar erros e navega
            st.session_state.id_bateria_erros   = id_b
            st.session_state.mats_bateria_erros = mats
            st.session_state.pagina = "registrar_erros"
            st.rerun()

    if col_b3.button("Cancelar", use_container_width=True):
        for k in ["bat_id", "bat_data", "bat_fonte", "bat_itens",
                  "form_cnt", "bat_data_input", "bat_fonte_input"]:
            st.session_state.pop(k, None)
        st.session_state.pagina = "dashboard"
        st.rerun()
