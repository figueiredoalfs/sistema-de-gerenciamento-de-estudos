"""
api_client.py
Camada de integração entre o Streamlit e o FastAPI (localhost:8000).

Uso nos módulos Streamlit:
    from api_client import api_login, api_registrar_bateria, ...

O token JWT é salvo em st.session_state.api_token após o login.
Se o servidor FastAPI não estiver rodando, as funções retornam None
e o Streamlit mantém o comportamento antigo via database.py.
"""

import requests
import streamlit as st

API_BASE = "http://localhost:8000"
TIMEOUT = 5  # segundos — não travar o Streamlit se a API estiver offline


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _api_online() -> bool:
    """Verifica se o FastAPI está respondendo."""
    try:
        r = requests.get(f"{API_BASE}/", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


# ── Autenticação ──────────────────────────────────────────────────────────────

def api_login(email: str, senha: str, nome: str = "") -> str | None:
    """
    Faz login no FastAPI. Retorna o access_token JWT ou None.
    Se o usuário ainda não existe no FastAPI, cria automaticamente (migração suave).
    """
    try:
        # OAuth2PasswordRequestForm exige form data com campos username/password
        r = requests.post(
            f"{API_BASE}/auth/login",
            data={"username": email, "password": senha},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("access_token")

        # Usuário não existe no FastAPI — cria automaticamente
        if r.status_code in (401, 404) and nome:
            reg = requests.post(
                f"{API_BASE}/auth/register",
                json={"nome": nome, "email": email, "password": senha},
                timeout=TIMEOUT,
            )
            if reg.status_code == 201:
                # Tenta login novamente com form data
                r2 = requests.post(
                    f"{API_BASE}/auth/login",
                    data={"username": email, "password": senha},
                    timeout=TIMEOUT,
                )
                if r2.status_code == 200:
                    return r2.json().get("access_token")
    except Exception:
        pass
    return None


# ── Bateria ───────────────────────────────────────────────────────────────────

def api_registrar_bateria(itens: list, fonte_padrao: str = "qconcursos") -> dict | None:
    """
    Envia bateria ao FastAPI.
    itens: lista de dicts com chaves: materia, subtopico, acertos, total, fonte (opcional)
    Retorna dict com bateria_id e proficiencias, ou None se falhar.
    """
    # Normaliza fontes para os valores aceitos pelo ENUM da API
    FONTES_VALIDAS = {
        "qconcursos", "tec", "prova_anterior_mesma_banca",
        "prova_anterior_outra_banca", "simulado", "quiz_ia", "manual", "calibracao", "curso",
    }
    MAPA_FONTES = {
        "guruja": "qconcursos", "gemini": "quiz_ia", "cei": "qconcursos",
        "alfacon": "qconcursos", "estrategia": "qconcursos",
    }

    questoes = []
    for item in itens:
        fonte_raw = str(item.get("fonte") or fonte_padrao or "qconcursos").strip().lower()
        fonte = MAPA_FONTES.get(fonte_raw, fonte_raw if fonte_raw in FONTES_VALIDAS else "qconcursos")
        questoes.append({
            "materia": item.get("materia", ""),
            "subtopico": item.get("subtopico") or None,
            "acertos": int(item.get("acertos", 0)),
            "total": int(item.get("total", 0)),
            "fonte": fonte,
        })

    try:
        r = requests.post(
            f"{API_BASE}/bateria",
            json={"questoes": questoes},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None


def api_listar_baterias(pagina: int = 1, por_pagina: int = 20) -> list:
    """Retorna lista de resumos de baterias do aluno logado."""
    try:
        r = requests.get(
            f"{API_BASE}/baterias",
            params={"pagina": pagina, "por_pagina": por_pagina},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


# ── Erros Críticos ────────────────────────────────────────────────────────────

def api_registrar_erro(
    materia: str,
    topico_texto: str,
    qtd_erros: int = 1,
    observacao: str = "",
    id_bateria: str = "",
) -> dict | None:
    """Registra erro crítico no FastAPI. status='pendente' por padrão."""
    try:
        r = requests.post(
            f"{API_BASE}/erro-critico",
            json={
                "materia": materia,
                "topico_texto": topico_texto,
                "qtd_erros": qtd_erros,
                "observacao": observacao or None,
                "id_bateria": id_bateria or None,
            },
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None


def api_listar_erros(status: str = None, materia: str = None) -> list:
    """Lista erros críticos com filtros opcionais."""
    params = {}
    if status:
        params["status"] = status
    if materia:
        params["materia"] = materia
    try:
        r = requests.get(
            f"{API_BASE}/erros-criticos",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("itens", [])
    except Exception:
        pass
    return []


def api_obter_desempenho(mes: int = None, ano: int = None, fontes: list = None) -> dict | None:
    """
    Retorna métricas de desempenho do aluno logado.
    Campos: total_questoes, total_acertos, perc_geral, por_materia (lista).
    Retorna None se a API estiver offline.
    """
    params = {}
    if mes:
        params["mes"] = mes
    if ano:
        params["ano"] = ano
    if fontes:
        params["fonte"] = fontes
    try:
        r = requests.get(
            f"{API_BASE}/desempenho",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_get_agenda(top: int = 14) -> list:
    """Retorna sessões priorizadas pelo algoritmo de scoring."""
    try:
        r = requests.get(
            f"{API_BASE}/agenda",
            params={"top": top},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("sessoes", [])
    except Exception:
        pass
    return []


def api_concluir_sessao(sessao_id: str, percentual: float = 0.0, duracao_real_min: int = 0) -> dict | None:
    """Marca sessão como concluída e registra desempenho. Retorna dict com reforco_inserido."""
    try:
        r = requests.patch(
            f"{API_BASE}/agenda/sessao/{sessao_id}/concluir",
            json={"percentual": percentual, "duracao_real_min": duracao_real_min},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_adiar_meta(dias: int = 7) -> bool:
    """Adia todas as sessoes pendentes em N dias."""
    try:
        r = requests.patch(
            f"{API_BASE}/agenda/adiar",
            params={"dias": dias},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except Exception:
        return False


def api_listar_tasks(tipo: str = None, status: str = None) -> list:
    """Lista study tasks do aluno com filtros opcionais."""
    params = {k: v for k, v in {"tipo": tipo, "status": status}.items() if v}
    try:
        r = requests.get(
            f"{API_BASE}/tasks",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("itens", [])
    except Exception:
        pass
    return []


def api_atualizar_status_erro(erro_id: str, novo_status: str) -> bool:
    """Atualiza status de um erro crítico. Retorna True se ok."""
    try:
        r = requests.patch(
            f"{API_BASE}/erro-critico/{erro_id}/status",
            json={"status": novo_status},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except Exception:
        return False
