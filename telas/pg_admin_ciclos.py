"""
telas/pg_admin_ciclos.py — Gerenciamento de ciclos de matérias por área.

Permite ao admin configurar quais matérias compõem o ciclo de cada área
e a ordem em que aparecem no plano inicial de estudos.
"""

import requests as _requests
import streamlit as st

_API_BASE = "http://localhost:8000"

AREAS = ["fiscal", "juridica", "policial"]


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _listar_ciclo(area: str) -> list:
    try:
        r = _requests.get(
            f"{_API_BASE}/admin/ciclos",
            params={"area": area},
            headers=_headers(),
            timeout=5,
        )
        if r.status_code == 200:
            return r.json().get("itens", [])
    except Exception:
        pass
    return []


def _listar_todos_subjects() -> list:
    """Retorna todos os Topicos nivel=0 disponíveis."""
    try:
        r = _requests.get(
            f"{_API_BASE}/admin/topicos",
            params={"nivel": 0},
            headers=_headers(),
            timeout=5,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def _adicionar(area: str, subject_id: str, ordem: int) -> bool:
    try:
        r = _requests.post(
            f"{_API_BASE}/admin/ciclos",
            json={"area": area, "subject_id": subject_id, "ordem": ordem},
            headers=_headers(),
            timeout=5,
        )
        return r.status_code == 201
    except Exception:
        return False


def _atualizar(ciclo_id: str, ordem: int = None, ativo: bool = None) -> bool:
    body = {}
    if ordem is not None:
        body["ordem"] = ordem
    if ativo is not None:
        body["ativo"] = ativo
    try:
        r = _requests.patch(
            f"{_API_BASE}/admin/ciclos/{ciclo_id}",
            json=body,
            headers=_headers(),
            timeout=5,
        )
        return r.status_code == 200
    except Exception:
        return False


def _remover(ciclo_id: str) -> bool:
    try:
        r = _requests.delete(
            f"{_API_BASE}/admin/ciclos/{ciclo_id}",
            headers=_headers(),
            timeout=5,
        )
        return r.status_code == 204
    except Exception:
        return False


def render():
    if st.session_state.get("usuario", {}).get("role") != "administrador":
        st.error("Acesso negado.")
        st.stop()

    st.markdown("## ⚙️ Ciclos de Matérias")
    st.caption("Configure quais matérias compõem o ciclo de cada área e a ordem de estudo.")

    # Seletor de área
    area = st.selectbox("Área", AREAS, key="ciclo_area_sel")

    itens = _listar_ciclo(area)

    st.markdown(f"### Ciclo atual — {area} ({len(itens)} matérias)")

    if not itens:
        st.info("Nenhuma matéria configurada para esta área.")
    else:
        for item in itens:
            col_ord, col_nome, col_ativo, col_up, col_down, col_rm = st.columns(
                [1, 4, 1, 1, 1, 1]
            )
            with col_ord:
                nova_ordem = st.number_input(
                    "Ordem",
                    min_value=0,
                    value=item["ordem"],
                    key=f"ord_{item['id']}",
                    label_visibility="collapsed",
                )
                if nova_ordem != item["ordem"]:
                    if _atualizar(item["id"], ordem=int(nova_ordem)):
                        st.rerun()

            with col_nome:
                st.markdown(
                    f"**{item['subject_nome'] or item['subject_id']}**",
                    unsafe_allow_html=False,
                )

            with col_ativo:
                ativo_atual = item["ativo"]
                novo_ativo = st.checkbox(
                    "Ativo",
                    value=ativo_atual,
                    key=f"ativo_{item['id']}",
                    label_visibility="collapsed",
                )
                if novo_ativo != ativo_atual:
                    if _atualizar(item["id"], ativo=novo_ativo):
                        st.rerun()

            with col_up:
                if st.button("↑", key=f"up_{item['id']}", help="Diminuir ordem"):
                    _atualizar(item["id"], ordem=max(0, item["ordem"] - 1))
                    st.rerun()

            with col_down:
                if st.button("↓", key=f"dn_{item['id']}", help="Aumentar ordem"):
                    _atualizar(item["id"], ordem=item["ordem"] + 1)
                    st.rerun()

            with col_rm:
                if st.button("🗑", key=f"rm_{item['id']}", help="Remover do ciclo"):
                    if _remover(item["id"]):
                        st.toast("Matéria removida do ciclo.")
                        st.rerun()

    st.divider()
    st.markdown("### Adicionar matéria ao ciclo")

    todos_subjects = _listar_todos_subjects()
    ids_no_ciclo = {i["subject_id"] for i in itens}
    disponiveis = [s for s in todos_subjects if s["id"] not in ids_no_ciclo]

    if not disponiveis:
        st.info("Todas as matérias disponíveis já estão no ciclo desta área.")
    else:
        opcoes = {s["nome"]: s["id"] for s in disponiveis}
        nome_sel = st.selectbox("Matéria", list(opcoes.keys()), key="ciclo_add_nome")
        nova_ord = st.number_input("Ordem", min_value=0, value=len(itens), key="ciclo_add_ordem")

        if st.button("Adicionar", type="primary", key="ciclo_btn_add"):
            ok = _adicionar(area, opcoes[nome_sel], int(nova_ord))
            if ok:
                st.toast(f"✅ {nome_sel} adicionada ao ciclo de {area}.")
                st.rerun()
            else:
                st.error("Erro ao adicionar. Verifique se a matéria já está no ciclo.")
