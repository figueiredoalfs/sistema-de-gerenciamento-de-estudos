"""
GET  /agenda?top=N   — sessões priorizadas
PATCH /agenda/sessao/{id}/concluir — marca sessão como concluída e registra desempenho
"""

import uuid
from datetime import datetime, timezone

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
    percentual: float = 0.0    # 0-100 — desempenho informado
    duracao_real_min: int = 0  # tempo real gasto


@router.get("")
def get_agenda(
    top: int = Query(default=14, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retorna top-N sessões priorizadas com score_breakdown."""
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
    Marca a sessão como concluída e registra o desempenho do aluno.

    Se percentual < 60, cria automaticamente uma sessão de reforço
    (flashcard_texto, 20 min) para o mesmo tópico no próximo pacote.
    """
    sessao = db.query(Sessao).filter(
        Sessao.id == sessao_id,
        Sessao.aluno_id == current_user.id,
    ).first()

    if not sessao:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    # Marca como concluída
    sessao.concluida = True
    sessao.data_concluida = datetime.now(timezone.utc)
    if body.duracao_real_min > 0:
        sessao.duracao_real_min = body.duracao_real_min

    # Registra proficiência se o aluno informou desempenho
    reforco_criado = False
    if body.percentual > 0 and sessao.topico_id:
        prof = Proficiencia(
            id=str(uuid.uuid4()),
            aluno_id=current_user.id,
            topico_id=sessao.topico_id,
            materia=sessao.topico.area if sessao.topico else None,
            acertos=0,
            total=0,
            percentual=body.percentual,
            fonte="manual",
            peso_fonte=PESO_POR_FONTE.get("manual", 0.8),
        )
        db.add(prof)

        # Reforço automático se desempenho < 60%
        if body.percentual < 60 and sessao.topico_id:
            reforco = Sessao(
                id=str(uuid.uuid4()),
                aluno_id=current_user.id,
                topico_id=sessao.topico_id,
                cronograma_id=sessao.cronograma_id,
                tipo="flashcard_texto",
                duracao_planejada_min=20,
                concluida=False,
            )
            db.add(reforco)
            reforco_criado = True

    db.commit()

    return {
        "ok": True,
        "sessao_id": sessao_id,
        "reforco_inserido": reforco_criado,
    }
