"""
routers/respostas.py

POST /questoes/{questao_id}/responder  — registra resposta de uma questão
GET  /desempenho/subtopicos            — desempenho do usuário por subtópico
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.questao import Questao
from app.models.resposta_questao import RespostaQuestao
from app.models.topico import Topico
from app.schemas.resposta_questao import (
    DesempenhoSubtopicoItem,
    DesempenhoSubtopicosResponse,
    ResponderQuestaoRequest,
    RespostaQuestaoResponse,
)

router = APIRouter(tags=["respostas"])


# ── Endpoint: registrar resposta ────────────────────────────────────────────────

@router.post(
    "/questoes/{questao_id}/responder",
    response_model=RespostaQuestaoResponse,
    status_code=201,
)
def responder_questao(
    questao_id: str,
    body: ResponderQuestaoRequest,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Registra a resposta do usuário autenticado para uma questão."""
    questao = db.query(Questao).filter(
        Questao.id == questao_id,
        Questao.ativo == True,
    ).first()

    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada ou inativa")

    correta = body.resposta_dada == questao.resposta_correta

    resposta = RespostaQuestao(
        aluno_id=usuario.id,
        questao_id=questao.id,
        subtopico_id=questao.subtopic_id,
        resposta_dada=body.resposta_dada,
        correta=correta,
    )
    db.add(resposta)
    db.commit()
    db.refresh(resposta)

    return resposta


# ── Endpoint: desempenho por subtópico ─────────────────────────────────────────

@router.get("/desempenho/subtopicos", response_model=DesempenhoSubtopicosResponse)
def get_desempenho_subtopicos(
    subtopico_id: Optional[str] = Query(None, description="Filtrar por subtópico específico"),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Retorna o desempenho do usuário agrupado por subtópico.
    Subtópicos com menor taxa de acerto aparecem primeiro.
    """
    # SQLite armazena Boolean como 0/1 — func.sum funciona diretamente
    q = (
        db.query(
            RespostaQuestao.subtopico_id,
            func.count(RespostaQuestao.id).label("respondidas"),
            func.sum(RespostaQuestao.correta).label("acertos"),
        )
        .filter(RespostaQuestao.aluno_id == usuario.id)
    )

    if subtopico_id:
        q = q.filter(RespostaQuestao.subtopico_id == subtopico_id)

    rows = q.group_by(RespostaQuestao.subtopico_id).all()

    # Busca nomes dos subtópicos de uma vez
    ids = [r.subtopico_id for r in rows]
    topicos_map: dict[str, str] = {}
    if ids:
        topicos = db.query(Topico.id, Topico.nome).filter(Topico.id.in_(ids)).all()
        topicos_map = {t.id: t.nome for t in topicos}

    subtopicos = []
    total_respondidas = 0
    total_acertos = 0

    for row in rows:
        respondidas = row.respondidas
        acertos = int(row.acertos or 0)
        taxa = round(acertos / respondidas * 100, 1) if respondidas > 0 else 0.0
        total_respondidas += respondidas
        total_acertos += acertos
        subtopicos.append(
            DesempenhoSubtopicoItem(
                subtopico_id=row.subtopico_id,
                subtopico_nome=topicos_map.get(row.subtopico_id, "Subtópico desconhecido"),
                respondidas=respondidas,
                acertos=acertos,
                taxa_acerto=taxa,
            )
        )

    # Mais fracos primeiro (uteis para priorização futura)
    subtopicos.sort(key=lambda x: x.taxa_acerto)

    taxa_geral = round(total_acertos / total_respondidas * 100, 1) if total_respondidas > 0 else 0.0

    return DesempenhoSubtopicosResponse(
        total_respondidas=total_respondidas,
        total_acertos=total_acertos,
        taxa_acerto_geral=taxa_geral,
        subtopicos=subtopicos,
    )
