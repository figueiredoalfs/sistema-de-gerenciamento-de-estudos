"""
telas/pg_perfil.py
Tela de perfil do usuario — dados pessoais, endereco, login e plano.
"""

import streamlit as st
from database import get_perfil, salvar_perfil, alterar_email, alterar_senha
from database import get_plataformas_ativas, salvar_plataformas_ativas
from config_fontes import GRUPOS_OPCIONAIS, GRUPOS_FONTE
from telas.components import page_title, _injetar_css


def render():
    _injetar_css()
    page_title("Meu Perfil", "Configurações da conta e preferências de estudo")

    usuario_id = st.session_state.usuario["id"]
    perfil = get_perfil(usuario_id)

    if not perfil:
        st.error("Nao foi possivel carregar o perfil.")
        return

    aba1, aba2, aba3, aba4, aba5 = st.tabs(
        ["Dados Pessoais", "Endereco", "Login & Senha", "Plano", "Plataformas"]
    )

    # ── ABA 1 — Dados pessoais ────────────────────────────────────────────────
    with aba1:
        st.markdown("#### Dados pessoais")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo", value=perfil.get("nome", ""), key="pf_nome")
            cpf  = st.text_input("CPF", value=perfil.get("cpf", ""), placeholder="000.000.000-00", key="pf_cpf")
        with col2:
            telefone = st.text_input("Telefone / WhatsApp", value=perfil.get("telefone", ""), placeholder="(00) 00000-0000", key="pf_tel")
            nascimento = st.text_input("Data de nascimento", value=perfil.get("data_nascimento", ""), placeholder="DD/MM/AAAA", key="pf_nasc")

        if st.button("Salvar dados pessoais", type="primary", key="btn_salvar_pessoal"):
            ok = salvar_perfil(usuario_id, {
                "nome": nome.strip(),
                "cpf": cpf.strip(),
                "telefone": telefone.strip(),
                "data_nascimento": nascimento.strip(),
            })
            if ok:
                st.session_state.usuario["nome"] = nome.strip()
                st.success("Dados atualizados com sucesso.")
            else:
                st.error("Nenhum campo para atualizar.")

    # ── ABA 2 — Endereco ─────────────────────────────────────────────────────
    with aba2:
        st.markdown("#### Endereco")
        col1, col2 = st.columns([1, 3])
        with col1:
            cep = st.text_input("CEP", value=perfil.get("cep", ""), placeholder="00000-000", key="pf_cep")
        with col2:
            endereco = st.text_input("Logradouro", value=perfil.get("endereco", ""), key="pf_end")

        col3, col4 = st.columns([1, 3])
        with col3:
            numero = st.text_input("Numero", value=perfil.get("numero", ""), key="pf_num")
        with col4:
            complemento = st.text_input("Complemento", value=perfil.get("complemento", ""), key="pf_comp")

        col5, col6, col7 = st.columns([2, 2, 1])
        with col5:
            bairro = st.text_input("Bairro", value=perfil.get("bairro", ""), key="pf_bairro")
        with col6:
            cidade = st.text_input("Cidade", value=perfil.get("cidade", ""), key="pf_cidade")
        with col7:
            estado = st.text_input("UF", value=perfil.get("estado", ""), max_chars=2, key="pf_uf")

        if st.button("Salvar endereco", type="primary", key="btn_salvar_end"):
            ok = salvar_perfil(usuario_id, {
                "cep": cep.strip(),
                "endereco": endereco.strip(),
                "numero": numero.strip(),
                "complemento": complemento.strip(),
                "bairro": bairro.strip(),
                "cidade": cidade.strip(),
                "estado": estado.strip().upper(),
            })
            if ok:
                st.success("Endereco atualizado com sucesso.")

    # ── ABA 3 — Login & Senha ─────────────────────────────────────────────────
    with aba3:
        st.markdown("#### Alterar e-mail")
        novo_email   = st.text_input("Novo e-mail", placeholder="novo@email.com", key="pf_email")
        conf_senha_e = st.text_input("Confirme sua senha atual", type="password", key="pf_senha_email")
        if st.button("Alterar e-mail", type="primary", key="btn_email"):
            if not novo_email or not conf_senha_e:
                st.warning("Preencha todos os campos.")
            else:
                resultado = alterar_email(usuario_id, novo_email, conf_senha_e)
                if resultado == "ok":
                    st.session_state.usuario["email"] = novo_email.strip().lower()
                    st.success("E-mail alterado com sucesso.")
                elif resultado == "senha_errada":
                    st.error("Senha atual incorreta.")
                else:
                    st.error("Este e-mail ja esta em uso.")

        st.divider()
        st.markdown("#### Alterar senha")
        senha_atual  = st.text_input("Senha atual", type="password", key="pf_s_atual")
        nova_senha   = st.text_input("Nova senha", type="password", key="pf_s_nova")
        conf_senha   = st.text_input("Confirmar nova senha", type="password", key="pf_s_conf")
        if st.button("Alterar senha", type="primary", key="btn_senha"):
            if not senha_atual or not nova_senha or not conf_senha:
                st.warning("Preencha todos os campos.")
            elif nova_senha != conf_senha:
                st.error("A nova senha e a confirmacao nao coincidem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                ok = alterar_senha(usuario_id, senha_atual, nova_senha)
                if ok:
                    st.success("Senha alterada com sucesso.")
                else:
                    st.error("Senha atual incorreta.")

    # ── ABA 4 — Plano ─────────────────────────────────────────────────────────
    with aba4:
        plano_atual = perfil.get("plano", "gratuito")
        badges = {
            "gratuito": ("Gratuito", "#3d5a80"),
            "basico":   ("Basico",   "#00a872"),
            "pro":      ("Pro",      "#00c48a"),
            "premium":  ("Premium",  "#f4a261"),
        }
        label, cor = badges.get(plano_atual, ("Desconhecido", "#888"))
        st.markdown(
            f'<div style="display:inline-block;background:{cor};color:#fff;'
            f'padding:4px 16px;border-radius:20px;font-weight:700;font-size:0.9rem;">'
            f'Plano atual: {label}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        planos = [
            ("basico",  "Basico",  "R$ 19,90/mes",  ["Acesso ilimitado", "Historico completo", "Analise de erros"]),
            ("pro",     "Pro",     "R$ 39,90/mes",  ["Tudo do Basico", "IA personalizada", "Simulados adaptativos"]),
            ("premium", "Premium", "R$ 69,90/mes",  ["Tudo do Pro", "Mentor IA dedicado", "Relatorios avancados"]),
        ]
        for col, (chave, nome, preco, items) in zip([col1, col2, col3], planos):
            with col:
                ativo = plano_atual == chave
                borda = "border: 2px solid #00c48a;" if ativo else "border: 1px solid #e0e0e0;"
                st.markdown(
                    f'<div style="padding:20px;border-radius:12px;{borda}text-align:center;">'
                    f'<h4 style="margin:0 0 4px 0;">{nome}</h4>'
                    f'<p style="font-size:1.2rem;font-weight:700;color:#00a872;margin:0 0 12px 0;">{preco}</p>'
                    + "".join(f'<p style="font-size:0.82rem;color:#555;margin:2px 0;">✓ {i}</p>' for i in items)
                    + f'</div>',
                    unsafe_allow_html=True,
                )
                if not ativo:
                    if st.button(f"Assinar {nome}", key=f"btn_plano_{chave}", use_container_width=True):
                        salvar_perfil(usuario_id, {"plano": chave})
                        st.success(f"Plano {nome} ativado! (ambiente de demonstracao)")
                        st.rerun()
                else:
                    st.markdown(
                        '<p style="text-align:center;color:#00c48a;font-weight:600;font-size:0.85rem;">Plano ativo</p>',
                        unsafe_allow_html=True,
                    )

    # ── ABA 5 — Plataformas ───────────────────────────────────────────────────
    with aba5:
        st.markdown("#### Tipos de plataforma que você usa")
        st.markdown(
            '<p style="color:#8ab0c8;font-size:0.85rem;">Isso define quais fontes aparecem '
            'ao lançar baterias de questões.</p>',
            unsafe_allow_html=True,
        )
        ativas = set(get_plataformas_ativas(usuario_id))
        novas  = set(ativas)

        for slug in GRUPOS_OPCIONAIS:
            info  = GRUPOS_FONTE[slug]
            ligado = slug in novas
            col_lbl, col_tog = st.columns([4, 1])
            col_lbl.markdown(
                f'<span style="color:#d0e4f0;font-weight:600;">{info["label"]}</span><br>'
                f'<span style="color:#8ab0c8;font-size:0.8rem;">{info["descricao"]}</span>',
                unsafe_allow_html=True,
            )
            novo_val = col_tog.checkbox(
                "Ativo", value=ligado, key=f"plat_tog_{slug}",
                label_visibility="collapsed",
            )
            if novo_val:
                novas.add(slug)
            else:
                novas.discard(slug)

        if st.button("Salvar plataformas", type="primary", key="btn_salvar_plat"):
            salvar_plataformas_ativas(usuario_id, list(novas))
            # Força recarga das fontes na próxima vez que abrir Lançar Bateria
            for k in list(st.session_state.keys()):
                if k.startswith("bat_"):
                    st.session_state.pop(k, None)
            st.success("Plataformas atualizadas.")
