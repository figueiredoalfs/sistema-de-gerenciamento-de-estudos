"""
GET /agenda?top=5
Retorna as sessões de estudo priorizadas pelo algoritmo de scoring.
Requer autenticação JWT (role: aluno ou admin).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.priorizacao import calcular_agenda

router = APIRouter(prefix="/agenda", tags=["agenda"])


@router.get("")
def get_agenda(
    top: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retorna top-N sessões priorizadas com score_breakdown.

    score_breakdown decompõe:
      - urgencia:    pressão do tempo até a prova
      - lacuna:      déficit de conhecimento + decay
      - peso:        importância no edital
      - fator_erros: erros críticos pendentes no tópico
    """
    aluno_id = current_user.id
    agenda = calcular_agenda(aluno_id=aluno_id, db=db, top=top)

    return {
        "aluno_id": aluno_id,
        "total": len(agenda),
        "sessoes": [
            {
                "sessao_id": s.sessao_id,
                "topico_id": s.topico_id,
                "topico_nome": s.topico_nome,
                "area": s.area,
                "tipo": s.tipo,
                "duracao_planejada_min": s.duracao_planejada_min,
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
