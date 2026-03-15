"""
POST /cronograma/gerar-semanal — gera o cronograma semanal de tasks do aluno.

Entrada (body opcional):
  { "week_number": 1 }

Resposta:
  {
    "week_number": 1,
    "tasks_semanais_calculadas": 15,
    "total_geradas": 15,
    "tasks_por_materia": { "Língua Portuguesa": 5, ... },
    "tasks": [ ...StudyTaskResponse... ]
  }
"""

from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.schemas.study_task import StudyTaskResponse
from app.services.gerador_cronograma import gerar_cronograma_semanal

router = APIRouter(prefix="/cronograma", tags=["cronograma"])


class GerarCronogramaRequest(BaseModel):
    week_number: int = 1


class CronogramaSemanalResponse(BaseModel):
    week_number: int
    tasks_semanais_calculadas: int
    total_geradas: int
    mensagem: Optional[str] = None
    tasks_por_materia: Dict[str, int]
    tasks: List[StudyTaskResponse]


@router.post("/gerar-semanal", response_model=CronogramaSemanalResponse, status_code=200)
def gerar_cronograma(
    body: GerarCronogramaRequest = GerarCronogramaRequest(),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Gera automaticamente a lista de tasks semanais com base na disponibilidade
    de estudo informada no onboarding (horas_por_dia × dias_por_semana).

    Tipo gerado: teoria.
    Distribuição: round-robin entre matérias para evitar repetição.

    Retorna total_geradas=0 se o cronograma da semana já foi gerado anteriormente.
    """
    tasks_semanais_calculadas = max(
        1,
        int((usuario.horas_por_dia or 1) * (usuario.dias_por_semana or 1)),
    )

    tasks = gerar_cronograma_semanal(
        db=db,
        aluno_id=usuario.id,
        week_number=body.week_number,
    )

    mensagem = None
    if not tasks:
        mensagem = f"Cronograma da semana {body.week_number} já existe ou não há subtópicos disponíveis."

    # Agrupa por nome da matéria para o resumo
    por_materia: Dict[str, int] = defaultdict(int)
    tasks_response: List[StudyTaskResponse] = []

    for t in tasks:
        nome_materia = t.subject.nome if t.subject else t.subject_id
        por_materia[nome_materia] += 1
        tasks_response.append(
            StudyTaskResponse(
                id=t.id,
                aluno_id=t.aluno_id,
                subject_id=t.subject_id,
                topic_id=t.topic_id,
                subtopic_id=t.subtopic_id,
                subject_nome=t.subject.nome if t.subject else None,
                topic_nome=t.topic.nome if t.topic else None,
                subtopic_nome=t.subtopic.nome if t.subtopic else None,
                tipo=t.tipo,
                status=t.status,
                week_number=t.week_number,
                order_in_week=t.order_in_week,
                created_at=t.created_at,
            )
        )

    return CronogramaSemanalResponse(
        week_number=body.week_number,
        tasks_semanais_calculadas=tasks_semanais_calculadas,
        total_geradas=len(tasks),
        mensagem=mensagem,
        tasks_por_materia=dict(por_materia),
        tasks=tasks_response,
    )
