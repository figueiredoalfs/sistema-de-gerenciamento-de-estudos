"""
GET   /agenda?top=N              — sessoes priorizadas
PATCH /agenda/sessao/{id}/concluir — marca concluida + registra desempenho
PATCH /agenda/adiar              — adia todas as sessoes pendentes em 7 dias
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.proficiencia import PESO_POR_FONTE, Proficiencia
from app.models.sessao import Sessao
from app.services.priorizacao import calcular_agenda

router = APIRouter(prefix="/agenda", tags=["agenda"])


class ConcluirBody(BaseModel):
    percentual: float = 0.0
    duracao_real_min: int = 0


@router.get("")
def get_agenda(
    top: int = Query(default=14, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retorna top-N sessoes priorizadas com score_breakdown."""
    agenda = calcular_agenda(aluno_id=current_user.id, db=db, top=top)
    return {
        "aluno_id": current_user.id,
        "total": len(agenda),
        "sessoes": [
            {
                "sessao_id": s.sessao_id,
                "topico_id": s.topico_id,
                "topico_nome": s.topico_nome,
                "area": s.area,
                "materia": s.materia,
                "topico_bloco": s.topico_bloco,
                "subtopico": s.subtopico,
                "tipo": s.tipo,
                "duracao_planejada_min": min(s.duracao_planejada_min, 50),
                "confianca": s.confianca,
                "score": s.score,
                "score_breakdown": {
                    "urgencia": s.breakdown.urgencia,
                    "lacuna": s.breakdown.lacuna,
                    "peso": s.breakdown.peso,
                    "fator_erros": s.breakdown.fator_erros,
                },
            }
            for s in agenda
        ],
    }


@router.patch("/sessao/{sessao_id}/concluir")
def concluir_sessao(
    sessao_id: str,
    body: ConcluirBody,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Marca sessao como concluida e registra desempenho.
    Se percentual < 60, insere sessao de reforco (flashcard_texto, 20 min).
    """
    sessao = db.query(Sessao).filter(
        Sessao.id == sessao_id,
        Sessao.aluno_id == current_user.id,
    ).first()

    if not sessao:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")

    sessao.concluida = True
    sessao.data_concluida = datetime.now(timezone.utc)
    if body.duracao_real_min > 0:
        sessao.duracao_real_min = body.duracao_real_min

    reforco_criado = False
    if body.percentual > 0 and sessao.topico_id:
        db.add(Proficiencia(
            id=str(uuid.uuid4()),
            aluno_id=current_user.id,
            topico_id=sessao.topico_id,
            materia=sessao.topico.area if sessao.topico else None,
            acertos=0,
            total=0,
            percentual=body.percentual,
            fonte="manual",
            peso_fonte=PESO_POR_FONTE.get("manual", 0.8),
        ))
        if body.percentual < 60:
            db.add(Sessao(
                id=str(uuid.uuid4()),
                aluno_id=current_user.id,
                topico_id=sessao.topico_id,
                cronograma_id=sessao.cronograma_id,
                tipo="flashcard_texto",
                duracao_planejada_min=20,
                concluida=False,
            ))
            reforco_criado = True

    db.commit()
    return {"ok": True, "sessao_id": sessao_id, "reforco_inserido": reforco_criado}


@router.patch("/adiar")
def adiar_meta(
    dias: int = Query(default=1, ge=1, le=3),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Adia todas as sessoes pendentes do aluno em N dias (default 7)."""
    sessoes = db.query(Sessao).filter(
        Sessao.aluno_id == current_user.id,
        Sessao.concluida == False,
    ).all()

    delta = timedelta(days=dias)
    agora = datetime.now(timezone.utc)
    for s in sessoes:
        if s.data_agendada:
            s.data_agendada = s.data_agendada + delta
        else:
            s.data_agendada = agora + delta

    db.commit()
    return {"ok": True, "sessoes_adiadas": len(sessoes), "dias": dias}
