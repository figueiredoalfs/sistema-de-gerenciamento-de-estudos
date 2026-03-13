"""
frontend/api_client.py
Funções HTTP para comunicação com o backend FastAPI.

Uso nos módulos Streamlit:
    from api_client import login, get_agenda, registrar_bateria, ...

O token JWT é salvo em st.session_state.api_token após o login.
"""

import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8080"
TIMEOUT = 5  # segundos

_FONTES_VALIDAS = {
    "qconcursos", "tec", "prova_anterior_mesma_banca",
    "prova_anterior_outra_banca", "simulado", "quiz_ia",
    "manual", "calibracao", "curso",
}
# Mapeia slugs do frontend (config_fontes.py) para os ENUMs aceitos pelo backend
_MAPA_FONTES = {
    "prova_mesma_banca":  "prova_anterior_mesma_banca",
    "prova_outra_banca":  "prova_anterior_outra_banca",
    "banco_questoes":     "qconcursos",
    "curso_online":       "curso",
    "mentoria":           "manual",
    "material_proprio":   "manual",
    "guruja":             "qconcursos",
    "gemini":             "quiz_ia",
    "cei":                "qconcursos",
    "alfacon":            "qconcursos",
    "estrategia":         "qconcursos",
}


def _headers() -> dict:
    token = st.session_state.get("api_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _normalizar_fonte(fonte: str) -> str:
    """Converte slug do frontend para ENUM aceito pelo backend."""
    f = str(fonte).strip().lower()
    return _MAPA_FONTES.get(f, f if f in _FONTES_VALIDAS else "qconcursos")


# ── Autenticação ───────────────────────────────────────────────────────────────

def login(email: str, senha: str) -> dict | None:
    """
    Login via OAuth2 PasswordFlow.
    Retorna {access_token, token_type, role, nome} ou None se falhar.
    """
    try:
        r = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": senha},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def register(nome: str, email: str, senha: str) -> bool:
    """Cria novo usuário. Retorna True se criado com sucesso (HTTP 201)."""
    try:
        r = requests.post(
            f"{BASE_URL}/auth/register",
            json={"nome": nome, "email": email, "password": senha},
            timeout=TIMEOUT,
        )
        return r.status_code == 201
    except Exception:
        return False


def get_me() -> dict | None:
    """
    Retorna perfil do usuário autenticado via GET /auth/me.
    Campos: id, nome, email, role, nivel_desafio, horas_por_dia, ativo.
    """
    try:
        r = requests.get(
            f"{BASE_URL}/auth/me",
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ── Onboarding ────────────────────────────────────────────────────────────────

def onboarding(data: dict) -> dict | None:
    """
    Envia dados de onboarding ao backend (POST /onboarding).
    data: {area, tem_edital, data_prova?, perfil, tempo_por_materia?,
           horas_por_dia, dias_por_semana}
    Retorna {aluno_id, cronograma_id, nivel_inicial, sessoes_geradas, mensagem}.
    """
    try:
        r = requests.post(
            f"{BASE_URL}/onboarding",
            json=data,
            headers=_headers(),
            timeout=30,
        )
        if r.status_code in (200, 201):
            return r.json()
    except Exception:
        pass
    return None


# ── Bateria ───────────────────────────────────────────────────────────────────

def registrar_bateria(itens: list, fonte_padrao: str = "qconcursos") -> dict | None:
    """
    Registra bateria de questões (POST /bateria).
    itens: [{materia, subtopico?, acertos, total, fonte?}]
    Retorna {bateria_id, total_questoes, proficiencias, mensagem} ou None.
    """
    questoes = []
    for item in itens:
        fonte = _normalizar_fonte(item.get("fonte") or fonte_padrao or "qconcursos")
        questoes.append({
            "materia":   item.get("materia", ""),
            "subtopico": item.get("subtopico") or None,
            "acertos":   int(item.get("acertos", 0)),
            "total":     int(item.get("total", 0)),
            "fonte":     fonte,
        })
    try:
        r = requests.post(
            f"{BASE_URL}/bateria",
            json={"questoes": questoes},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None


def listar_baterias(pagina: int = 1, por_pagina: int = 50) -> list:
    """
    Lista resumos de baterias do aluno logado (GET /baterias).
    Retorna lista de {bateria_id, data, total_questoes, total_acertos,
                      percentual_geral, materias}.
    """
    try:
        r = requests.get(
            f"{BASE_URL}/baterias",
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

def registrar_erro(
    materia: str,
    topico_texto: str,
    qtd_erros: int = 1,
    observacao: str = "",
    id_bateria: str = "",
) -> dict | None:
    """Registra erro crítico (POST /erro-critico)."""
    try:
        r = requests.post(
            f"{BASE_URL}/erro-critico",
            json={
                "materia":      materia,
                "topico_texto": topico_texto,
                "qtd_erros":    qtd_erros,
                "observacao":   observacao or None,
                "id_bateria":   id_bateria or None,
            },
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None


def listar_erros(status: str = None, materia: str = None) -> list:
    """
    Lista erros críticos (GET /erros-criticos).
    Retorna lista de {id, materia, topico_texto, qtd_erros,
                      observacao, status, data, id_bateria}.
    status aceito: pendente | em_revisao | resolvido
    """
    params = {}
    if status:
        params["status"] = status
    if materia:
        params["materia"] = materia
    try:
        r = requests.get(
            f"{BASE_URL}/erros-criticos",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("itens", [])
    except Exception:
        pass
    return []


def atualizar_status_erro(erro_id: str, novo_status: str) -> bool:
    """
    Atualiza status de um erro crítico (PATCH /erro-critico/{id}/status).
    novo_status: pendente | em_revisao | resolvido
    """
    try:
        r = requests.patch(
            f"{BASE_URL}/erro-critico/{erro_id}/status",
            json={"status": novo_status},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except Exception:
        return False


# ── Desempenho ────────────────────────────────────────────────────────────────

def obter_desempenho(mes: int = None, ano: int = None, fontes: list = None) -> dict | None:
    """
    Retorna métricas de desempenho (GET /desempenho).
    Retorna {total_questoes, total_acertos, perc_geral,
             por_materia: [{materia, realizadas, acertos, perc,
                            tend_perc_atual, tend_perc_anterior}]}
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
            f"{BASE_URL}/desempenho",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ── Agenda ────────────────────────────────────────────────────────────────────

def get_agenda(top: int = 14) -> list:
    """
    Retorna sessões priorizadas (GET /agenda).
    Retorna lista de {sessao_id, topico_nome, area, tipo,
                      duracao_planejada_min, score, ...}.
    """
    try:
        r = requests.get(
            f"{BASE_URL}/agenda",
            params={"top": top},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("sessoes", [])
    except Exception:
        pass
    return []


def concluir_sessao(sessao_id: str, percentual: float = 0.0, duracao_real_min: int = 0) -> dict | None:
    """
    Marca sessão como concluída (PATCH /agenda/sessao/{id}/concluir).
    Retorna {reforco_inserido: bool} ou None.
    """
    try:
        r = requests.patch(
            f"{BASE_URL}/agenda/sessao/{sessao_id}/concluir",
            json={"percentual": percentual, "duracao_real_min": duracao_real_min},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def adiar_meta(dias: int = 7) -> bool:
    """Adia todas as sessões pendentes em N dias (PATCH /agenda/adiar)."""
    try:
        r = requests.patch(
            f"{BASE_URL}/agenda/adiar",
            params={"dias": dias},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except Exception:
        return False


# ── Conteúdo IA ───────────────────────────────────────────────────────────────

def gerar_resumo(topico: str) -> str | None:
    """Gera resumo do tópico com IA (POST /conteudo/resumo)."""
    try:
        r = requests.post(
            f"{BASE_URL}/conteudo/resumo",
            json={"topico": topico},
            headers=_headers(),
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("resumo")
    except Exception:
        pass
    return None


def gerar_flashcards(topico: str) -> list:
    """Gera 5 flashcards do tópico com IA (POST /conteudo/flashcards)."""
    try:
        r = requests.post(
            f"{BASE_URL}/conteudo/flashcards",
            json={"topico": topico},
            headers=_headers(),
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("flashcards", [])
    except Exception:
        pass
    return []


def gerar_exemplo(topico: str) -> str | None:
    """Gera exemplo prático do tópico com IA (POST /conteudo/exemplo)."""
    try:
        r = requests.post(
            f"{BASE_URL}/conteudo/exemplo",
            json={"topico": topico},
            headers=_headers(),
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("exemplo")
    except Exception:
        pass
    return None
