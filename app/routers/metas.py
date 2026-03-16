"""
Rotas de Metas pedagógicas.

POST /metas/gerar              — gera nova Meta com tasks pedagógicas
GET  /metas                    — lista todas as metas do aluno (abertas + histórico)
GET  /metas/{meta_id}          — detalhes de uma meta específica
PATCH /metas/{meta_id}/encerrar — encerra manualmente uma meta aberta
"""

from typing import List, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.meta import Meta
from app.models.study_task import StudyTask
from app.schemas.meta import GoalActiveResponse, MetaGerarRequest, MetaListResponse, MetaResponse
from app.schemas.study_task import StudyTaskResponse
from app.services.engine_pedagogica import gerar_meta

router = APIRouter(prefix="/metas", tags=["metas"])


# ---------------------------------------------------------------------------
# Helpers de serialização
# ---------------------------------------------------------------------------

def _task_to_response(t: StudyTask) -> StudyTaskResponse:
    return StudyTaskResponse(
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
        questoes_json=t.questoes_json,
        task_code=t.task_code,
        week_number=t.week_number,
        order_in_week=t.order_in_week,
        goal_id=t.goal_id,
        created_at=t.created_at,
    )


def _meta_to_response(meta: Meta) -> MetaResponse:
    return MetaResponse(
        id=meta.id,
        aluno_id=meta.aluno_id,
        numero_semana=meta.numero_semana,
        tasks_meta=meta.tasks_meta,
        tasks_concluidas=meta.tasks_concluidas,
        status=meta.status,
        created_at=meta.created_at,
        tasks=[_task_to_response(t) for t in (meta.tasks or [])],
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/gerar", response_model=MetaResponse, status_code=201)
def gerar(
    body: MetaGerarRequest = MetaGerarRequest(),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Gera uma nova Meta pedagógica para o aluno autenticado.

    - Calcula tasks_meta = int(horas_por_dia × dias_por_semana).
    - Prioriza: revisões > reforços > novos subtópicos.
    - Alterna matérias automaticamente (round-robin).
    - Retorna 409 se já existe uma Meta aberta.
    - Retorna 422 se todos os subtópicos estiverem dominados.
    """
    meta = gerar_meta(db=db, aluno_id=usuario.id)
    return _meta_to_response(meta)


@router.get("", response_model=MetaListResponse)
def listar(
    status: Optional[str] = Query(
        default=None,
        description="Filtrar por status: 'aberta' ou 'encerrada'. Omitir retorna todas.",
    ),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Lista todas as metas do aluno, incluindo o histórico de metas encerradas.
    Use ?status=encerrada para ver apenas o histórico arquivado.
    """
    query = db.query(Meta).filter(Meta.aluno_id == usuario.id)
    if status in ("aberta", "encerrada"):
        query = query.filter(Meta.status == status)
    metas = query.order_by(Meta.numero_semana.desc()).all()

    abertas = sum(1 for m in metas if m.status == "aberta")
    encerradas = sum(1 for m in metas if m.status == "encerrada")

    return MetaListResponse(
        total=len(metas),
        abertas=abertas,
        encerradas=encerradas,
        metas=[_meta_to_response(m) for m in metas],
    )


@router.get("/active", response_model=GoalActiveResponse)
def meta_ativa(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Retorna a meta ativa com progresso calculado via agregação SQL."""
    meta = (
        db.query(Meta)
        .filter(Meta.aluno_id == usuario.id, Meta.status == "aberta")
        .first()
    )
    if not meta:
        raise HTTPException(status_code=404, detail="Nenhuma meta ativa.")

    row = db.query(
        sa.func.count(StudyTask.id).label("tasks_total"),
        sa.func.count(
            sa.case((StudyTask.status == "completed", StudyTask.id))
        ).label("tasks_completed"),
    ).filter(StudyTask.goal_id == meta.id).one()

    total = row.tasks_total or 0
    completed = row.tasks_completed or 0
    pct = int(completed / max(1, total) * 100)

    return GoalActiveResponse(
        goal_id=meta.id,
        tasks_total=total,
        tasks_completed=completed,
        progress_percentage=pct,
    )


@router.get("/{meta_id}", response_model=MetaResponse)
def detalhar(
    meta_id: str,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Retorna os detalhes de uma meta específica, incluindo todas as suas tasks.
    Permite ao aluno consultar o histórico de qualquer meta passada.
    """
    meta = (
        db.query(Meta)
        .filter(Meta.id == meta_id, Meta.aluno_id == usuario.id)
        .first()
    )
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada.")
    return _meta_to_response(meta)


@router.patch("/{meta_id}/encerrar", response_model=MetaResponse)
def encerrar(
    meta_id: str,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Encerra manualmente uma meta aberta, arquivando-a no histórico.
    Tasks pendentes são mantidas; apenas o status da meta muda.
    """
    meta = (
        db.query(Meta)
        .filter(Meta.id == meta_id, Meta.aluno_id == usuario.id)
        .first()
    )
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada.")
    if meta.status == "encerrada":
        raise HTTPException(status_code=409, detail="Meta já está encerrada.")

    meta.status = "encerrada"
    db.commit()
    db.refresh(meta)
    return _meta_to_response(meta)
