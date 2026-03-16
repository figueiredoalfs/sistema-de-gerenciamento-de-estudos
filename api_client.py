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


def api_get_questoes_task(task_id: str, subject_id: str = None, questao_ids: list[str] = None) -> list:
    """Busca as questões de uma task diagnóstica via endpoint dedicado."""
    try:
        r = requests.get(
            f"{API_BASE}/tasks/{task_id}/questoes",
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def api_responder_questao(questao_id: str, resposta_dada: str) -> dict | None:
    """Registra resposta do aluno para uma questão da Meta 00."""
    try:
        r = requests.post(
            f"{API_BASE}/questoes/{questao_id}/responder",
            json={"resposta_dada": resposta_dada},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None


def api_iniciar_task(task_id: str) -> dict | None:
    """Marca uma StudyTask como in_progress."""
    try:
        r = requests.patch(
            f"{API_BASE}/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_concluir_task(task_id: str) -> dict | None:
    """Marca uma StudyTask como completed e retorna o resultado com tarefas_geradas."""
    try:
        r = requests.patch(
            f"{API_BASE}/tasks/{task_id}/status",
            json={"status": "completed"},
            headers=_headers(),
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_gerar_meta() -> dict | None:
    """Gera uma nova meta semanal de estudo."""
    try:
        r = requests.post(
            f"{API_BASE}/metas/gerar",
            json={},
            headers=_headers(),
            timeout=15,
        )
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None


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


def api_obter_evolucao() -> list:
    """Retorna a evolução mensal de desempenho por matéria."""
    try:
        r = requests.get(
            f"{API_BASE}/desempenho/evolucao",
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def api_atualizar_perfil(dados: dict) -> dict | None:
    """Atualiza campos do perfil (nome, email, nivel_desafio, horas_por_dia, dias_por_semana, area)."""
    try:
        r = requests.patch(
            f"{API_BASE}/auth/me",
            json=dados,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_alterar_senha(senha_atual: str, nova_senha: str) -> dict:
    """Altera senha do usuário. Retorna dict com 'ok' ou 'erro'."""
    try:
        r = requests.post(
            f"{API_BASE}/auth/alterar-senha",
            json={"senha_atual": senha_atual, "nova_senha": nova_senha},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return {"ok": True}
        return {"ok": False, "erro": r.json().get("detail", "Erro desconhecido")}
    except Exception:
        return {"ok": False, "erro": "API indisponível"}


def api_obter_explicacao(topico_id: str) -> str | None:
    """
    Busca a explicação de um subtópico (cache ou geração via IA).
    Timeout maior pois a primeira chamada pode levar até ~15s (geração pela IA).
    """
    try:
        r = requests.get(
            f"{API_BASE}/explicacoes/topico/{topico_id}",
            headers=_headers(),
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("content")
    except Exception:
        pass
    return None


# ── Task Conteudo & Cronograma ────────────────────────────────────────────────

def api_get_tasks_hoje() -> dict:
    """Retorna tasks do dia limitadas por horas_por_dia do usuário."""
    try:
        r = requests.get(
            f"{API_BASE}/tasks/today",
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"daily_limit": 0, "tasks": []}


def api_get_meta_ativa() -> dict | None:
    """Retorna meta ativa com progresso calculado."""
    try:
        r = requests.get(
            f"{API_BASE}/metas/active",
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_listar_cronograma() -> list:
    """Retorna tasks do cronograma semanal ordenadas por numero_cronograma."""
    try:
        r = requests.get(
            f"{API_BASE}/tasks",
            params={"cronograma": "true"},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("itens", [])
    except Exception:
        pass
    return []


def api_obter_task_conteudo(task_code: str) -> dict | None:
    """Retorna conteúdo compartilhado da task (objetivo, instrucoes). Gera via IA se necessário."""
    try:
        r = requests.get(
            f"{API_BASE}/task-conteudo/{task_code}",
            headers=_headers(),
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def api_gerar_pdf_task(task_code: str) -> str | None:
    """Gera (ou retorna cache de) PDF do subtópico via IA."""
    try:
        r = requests.post(
            f"{API_BASE}/task-conteudo/{task_code}/gerar-pdf",
            headers=_headers(),
            timeout=35,
        )
        if r.status_code == 200:
            return r.json().get("conteudo_pdf")
    except Exception:
        pass
    return None


def api_listar_videos_task(task_code: str) -> list:
    """Lista vídeos cadastrados para a task, ordenados por avaliação."""
    try:
        r = requests.get(
            f"{API_BASE}/task-conteudo/{task_code}/videos",
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def api_buscar_videos_task(task_code: str) -> list:
    """Solicita à IA que busque vídeos para a task e salva no banco."""
    try:
        r = requests.post(
            f"{API_BASE}/task-conteudo/{task_code}/videos/buscar",
            headers=_headers(),
            timeout=35,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def api_avaliar_video(video_id: str, nota: int) -> dict | None:
    """Registra ou atualiza a avaliação (1–5) de um vídeo pelo aluno."""
    try:
        r = requests.post(
            f"{API_BASE}/task-videos/{video_id}/avaliar",
            json={"nota": nota},
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None
