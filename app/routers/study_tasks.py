"""
routers/study_tasks.py

POST  /tasks              — cria task de estudo
GET   /tasks              — lista tasks do usuário (filtros: tipo, status)
PATCH /tasks/{id}/status  — atualiza status da task
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

TIPOS_VALIDOS = {
    "study", "questions", "review", "diagnostico",
    "teoria", "revisao", "questionario", "simulado", "reforco",
}

import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.questao import Questao
from app.models.study_task import StudyTask
from app.models.topico import Topico
from app.schemas.questao import QuestaoResponse
from app.schemas.study_task import (
    StudyTaskCreate,
    StudyTaskListResponse,
    StudyTaskResponse,
    StudyTaskStatusUpdate,
    TaskGeradaItem,
)
from app.services.desempenho_diagnostico import calcular_e_salvar_desempenho_diagnostico
from app.services.plano_pos_diagnostico import gerar_tasks_pos_diagnostico

router = APIRouter(tags=["tasks"])


# ── Helpers ─────────────────────────────────────────────────────────────────────

def _get_topico(db: Session, topico_id: str, nivel: int) -> Topico:
    """Busca um tópico pelo id e valida o nível esperado. Lança 404 se não encontrar."""
    topico = db.query(Topico).filter(
        Topico.id == topico_id,
        Topico.nivel == nivel,
        Topico.ativo == True,
    ).first()
    niveis = {0: "subject", 1: "topic", 2: "subtopic"}
    if not topico:
        raise HTTPException(
            status_code=404,
            detail=f"{niveis[nivel]} '{topico_id}' não encontrado ou inativo",
        )
    return topico


def _validar_hierarquia(db: Session, subject_id: str, topic_id: str, subtopic_id: str):
    """Valida que topic é filho de subject e subtopic é filho de topic."""
    subject = _get_topico(db, subject_id, nivel=0)
    topic = _get_topico(db, topic_id, nivel=1)
    subtopic = _get_topico(db, subtopic_id, nivel=2)

    if topic.parent_id != subject.id:
        raise HTTPException(status_code=422, detail="topic não pertence ao subject informado")
    if subtopic.parent_id != topic.id:
        raise HTTPException(status_code=422, detail="subtopic não pertence ao topic informado")

    return subject, topic, subtopic


def _to_response(task: StudyTask, desempenho=None, tarefas_geradas=None) -> StudyTaskResponse:
    geradas = None
    if tarefas_geradas:
        geradas = [
            TaskGeradaItem(
                id=t.id,
                subject_id=t.subject_id,
                topic_id=t.topic_id,
                subtopic_id=t.subtopic_id,
                subject_nome=t.subject.nome if t.subject else None,
                topic_nome=t.topic.nome if t.topic else None,
                subtopic_nome=t.subtopic.nome if t.subtopic else None,
                tipo=t.tipo,
                status=t.status,
            )
            for t in tarefas_geradas
        ]
    return StudyTaskResponse(
        id=task.id,
        aluno_id=task.aluno_id,
        subject_id=task.subject_id,
        topic_id=task.topic_id,
        subtopic_id=task.subtopic_id,
        subject_nome=task.subject.nome if task.subject else None,
        topic_nome=task.topic.nome if task.topic else None,
        subtopic_nome=task.subtopic.nome if task.subtopic else None,
        tipo=task.tipo,
        status=task.status,
        questoes_json=task.questoes_json,
        created_at=task.created_at,
        desempenho_subtopicos=desempenho,
        tarefas_geradas=geradas,
    )


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/tasks", response_model=StudyTaskResponse, status_code=201)
def criar_task(
    body: StudyTaskCreate,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Cria uma task de estudo para o usuário autenticado."""
    # Tasks diagnósticas operam no nível da matéria; topic/subtopic são opcionais
    if body.tipo != "diagnostico":
        if not body.topic_id or not body.subtopic_id:
            raise HTTPException(
                status_code=422,
                detail="topic_id e subtopic_id são obrigatórios para tasks do tipo study, questions e review.",
            )
        _validar_hierarquia(db, body.subject_id, body.topic_id, body.subtopic_id)
    else:
        _get_topico(db, body.subject_id, nivel=0)

    task = StudyTask(
        aluno_id=usuario.id,
        subject_id=body.subject_id,
        topic_id=body.topic_id,
        subtopic_id=body.subtopic_id,
        tipo=body.tipo,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return _to_response(task)


@router.get("/tasks", response_model=StudyTaskListResponse)
def listar_tasks(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    status: Optional[str] = Query(None, description="Filtrar por status: pending, in_progress, completed"),
    cronograma: Optional[bool] = Query(None, description="Se True, retorna apenas tasks do cronograma ordenadas"),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Lista todas as tasks do usuário autenticado, com filtros opcionais."""
    q = db.query(StudyTask).filter(StudyTask.aluno_id == usuario.id)

    if tipo:
        if tipo not in TIPOS_VALIDOS:
            raise HTTPException(status_code=422, detail=f"tipo inválido. Use: {', '.join(sorted(TIPOS_VALIDOS))}")
        q = q.filter(StudyTask.tipo == tipo)

    if status:
        if status not in {"pending", "in_progress", "completed"}:
            raise HTTPException(status_code=422, detail="status inválido. Use: pending, in_progress, completed")
        q = q.filter(StudyTask.status == status)

    if cronograma:
        q = q.filter(StudyTask.numero_cronograma.isnot(None)).order_by(StudyTask.numero_cronograma.asc())
        tasks = q.all()
    else:
        tasks = q.order_by(StudyTask.created_at.desc()).all()

    return StudyTaskListResponse(
        total=len(tasks),
        itens=[_to_response(t) for t in tasks],
    )


@router.patch("/tasks/{task_id}/status", response_model=StudyTaskResponse)
def atualizar_status(
    task_id: str,
    body: StudyTaskStatusUpdate,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Atualiza o status de uma task do usuário autenticado."""
    task = db.query(StudyTask).filter(
        StudyTask.id == task_id,
        StudyTask.aluno_id == usuario.id,
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")

    ja_concluida = task.status == "completed"
    task.status = body.status
    db.commit()
    db.refresh(task)

    desempenho = None
    tarefas_geradas = None
    if task.tipo == "diagnostico" and body.status == "completed" and not ja_concluida:
        desempenho = calcular_e_salvar_desempenho_diagnostico(usuario.id, task, db)
        tarefas_geradas = gerar_tasks_pos_diagnostico(
            aluno_id=usuario.id,
            desempenho=desempenho,
            db=db,
        )

    return _to_response(task, desempenho, tarefas_geradas)


@router.get("/tasks/{task_id}/questoes", response_model=list[QuestaoResponse])
def listar_questoes_task(
    task_id: str,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Retorna as questões de uma task diagnóstica pelo IDs armazenados em questoes_json."""
    task = db.query(StudyTask).filter(
        StudyTask.id == task_id,
        StudyTask.aluno_id == usuario.id,
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    if not task.questoes_json:
        return []

    try:
        ids = json.loads(task.questoes_json)
    except (ValueError, TypeError):
        return []

    if not ids:
        return []

    questoes = db.query(Questao).filter(Questao.id.in_(ids), Questao.ativo == True).all()
    return [QuestaoResponse.model_validate(q) for q in questoes]
