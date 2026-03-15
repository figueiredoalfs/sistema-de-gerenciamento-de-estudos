"""
telas/pg_perfil.py
Tela de perfil do usuario — dados de estudo e login.
"""

import streamlit as st

from api_client import api_alterar_senha, api_atualizar_perfil
from telas.components import _injetar_css, page_title

AREAS = ["Fiscal", "Jurídica", "Policial", "TI", "Saúde", "Outro"]
NIVEIS = ["conservador", "moderado", "agressivo"]


def render():
    _injetar_css()
    page_title("Meu Perfil", "Configurações da conta e preferências de estudo")

    usuario = st.session_state.usuario

    aba1, aba2 = st.tabs(["Dados de Estudo", "Segurança"])

    # ── ABA 1 — Dados de estudo ───────────────────────────────────────────────
    with aba1:
        st.markdown("#### Dados da conta")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo", value=usuario.get("nome", ""), key="pf_nome")
        with col2:
            email = st.text_input("E-mail", value=usuario.get("email", ""), key="pf_email")

        st.markdown("#### Preferências de estudo")
        col3, col4 = st.columns(2)
        with col3:
            area_atual = usuario.get("area", "Fiscal") or "Fiscal"
            area_idx   = AREAS.index(area_atual) if area_atual in AREAS else 0
            area = st.selectbox("Área de concurso", AREAS, index=area_idx, key="pf_area")

            nivel_atual = usuario.get("nivel_desafio", "moderado") or "moderado"
            nivel_idx   = NIVEIS.index(nivel_atual) if nivel_atual in NIVEIS else 1
            nivel = st.selectbox("Nível de desafio", NIVEIS, index=nivel_idx, key="pf_nivel")
        with col4:
            horas = st.number_input(
                "Horas de estudo por dia",
                min_value=0.5, max_value=16.0, step=0.5,
                value=float(usuario.get("horas_por_dia") or 3.0),
                key="pf_horas",
            )
            dias = st.number_input(
                "Dias de estudo por semana",
                min_value=1, max_value=7, step=1,
                value=int(usuario.get("dias_por_semana") or 5),
                key="pf_dias",
            )

        if st.button("Salvar preferências", type="primary", key="btn_salvar_estudo"):
            dados = {
                "nome": nome.strip(),
                "email": email.strip(),
                "area": area,
                "nivel_desafio": nivel,
                "horas_por_dia": horas,
                "dias_por_semana": float(dias),
            }
            resultado = api_atualizar_perfil(dados)
            if resultado:
                st.session_state.usuario["nome"]          = resultado["nome"]
                st.session_state.usuario["email"]         = resultado["email"]
                st.session_state.usuario["nivel_desafio"] = resultado["nivel_desafio"]
                st.session_state.usuario["horas_por_dia"] = resultado["horas_por_dia"]
                st.session_state.usuario["area"]          = area
                st.success("Perfil atualizado com sucesso.")
            else:
                st.error("Não foi possível salvar. Verifique se o e-mail não está em uso.")

    # ── ABA 2 — Segurança ─────────────────────────────────────────────────────
    with aba2:
        st.markdown("#### Alterar senha")
        senha_atual = st.text_input("Senha atual", type="password", key="pf_s_atual")
        nova_senha  = st.text_input("Nova senha (mín. 6 caracteres)", type="password", key="pf_s_nova")
        conf_senha  = st.text_input("Confirmar nova senha", type="password", key="pf_s_conf")

        if st.button("Alterar senha", type="primary", key="btn_senha"):
            if not senha_atual or not nova_senha or not conf_senha:
                st.warning("Preencha todos os campos.")
            elif nova_senha != conf_senha:
                st.error("A nova senha e a confirmação não coincidem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                res = api_alterar_senha(senha_atual, nova_senha)
                if res.get("ok"):
                    st.success("Senha alterada com sucesso.")
                else:
                    st.error(res.get("erro", "Erro ao alterar senha."))
