import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.aluno import Aluno
from app.models.topico import Topico
from app.schemas.conhecimento import (
    KnowledgeUpdate,
    SubjectCreate,
    SubjectResponse,
    SubtopicCreate,
    SubtopicResponse,
    TopicCreate,
    TopicResponse,
)

router = APIRouter(tags=["conhecimento"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, topico_id: str, nivel: int | None = None) -> Topico:
    q = db.query(Topico).filter(Topico.id == topico_id)
    if nivel is not None:
        q = q.filter(Topico.nivel == nivel)
    topico = q.first()
    if not topico:
        labels = {0: "Subject", 1: "Topic", 2: "Subtopic"}
        label = labels.get(nivel, "Topico") if nivel is not None else "Topico"
        raise HTTPException(status_code=404, detail=f"{label} nao encontrado")
    return topico


def _build_subject_response(subject: Topico, db: Session) -> SubjectResponse:
    topics = (
        db.query(Topico)
        .filter(Topico.parent_id == subject.id, Topico.nivel == 1, Topico.ativo == True)
        .order_by(Topico.nome)
        .all()
    )
    topic_responses = []
    for topic in topics:
        subtopics = (
            db.query(Topico)
            .filter(Topico.parent_id == topic.id, Topico.nivel == 2, Topico.ativo == True)
            .order_by(Topico.nome)
            .all()
        )
        topic_responses.append(
            TopicResponse(
                id=topic.id,
                nome=topic.nome,
                descricao=topic.descricao,
                peso_edital=topic.peso_edital,
                ativo=topic.ativo,
                subtopics=[
                    SubtopicResponse(
                        id=s.id,
                        nome=s.nome,
                        descricao=s.descricao,
                        decay_rate=s.decay_rate,
                        ativo=s.ativo,
                    )
                    for s in subtopics
                ],
            )
        )
    return SubjectResponse(
        id=subject.id,
        nome=subject.nome,
        area=subject.area,
        banca=subject.banca,
        descricao=subject.descricao,
        peso_edital=subject.peso_edital,
        ativo=subject.ativo,
        topics=topic_responses,
    )


# ─── Subjects ─────────────────────────────────────────────────────────────────

@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def criar_subject(
    body: SubjectCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cria uma nova matéria (subject)."""
    topico = Topico(
        id=str(uuid.uuid4()),
        nome=body.nome,
        nivel=0,
        area=body.area or body.nome,
        banca=body.banca,
        descricao=body.descricao,
        peso_edital=body.peso_edital,
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return _build_subject_response(topico, db)


@router.get("/subjects", response_model=List[SubjectResponse])
def listar_subjects(
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    """Lista todas as matérias com seus tópicos e subtópicos."""
    subjects = (
        db.query(Topico)
        .filter(Topico.nivel == 0, Topico.ativo == True)
        .order_by(Topico.nome)
        .all()
    )
    return [_build_subject_response(s, db) for s in subjects]


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def detalhe_subject(
    subject_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    """Retorna uma matéria com toda a sua árvore de tópicos e subtópicos."""
    subject = _get_or_404(db, subject_id, nivel=0)
    return _build_subject_response(subject, db)


@router.patch("/subjects/{subject_id}", response_model=SubjectResponse)
def editar_subject(
    subject_id: str,
    body: KnowledgeUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de uma matéria."""
    subject = _get_or_404(db, subject_id, nivel=0)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return _build_subject_response(subject, db)


@router.delete("/subjects/{subject_id}", status_code=204)
def deletar_subject(
    subject_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: desativa uma matéria (soft-delete). Rejeita se tiver tópicos ativos."""
    subject = _get_or_404(db, subject_id, nivel=0)
    filhos_ativos = db.query(Topico).filter(
        Topico.parent_id == subject_id, Topico.ativo == True
    ).count()
    if filhos_ativos:
        raise HTTPException(
            status_code=400,
            detail=f"Impossivel desativar: subject possui {filhos_ativos} topico(s) ativo(s)",
        )
    subject.ativo = False
    db.commit()


# ─── Topics ───────────────────────────────────────────────────────────────────

@router.post("/topics", response_model=TopicResponse, status_code=201)
def criar_topic(
    body: TopicCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cria um tópico dentro de um subject."""
    subject = _get_or_404(db, body.subject_id, nivel=0)
    topico = Topico(
        id=str(uuid.uuid4()),
        nome=body.nome,
        nivel=1,
        parent_id=subject.id,
        area=subject.area,
        descricao=body.descricao,
        peso_edital=body.peso_edital,
        decay_rate=subject.decay_rate,
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return TopicResponse(
        id=topico.id,
        nome=topico.nome,
        descricao=topico.descricao,
        peso_edital=topico.peso_edital,
        ativo=topico.ativo,
        subtopics=[],
    )


@router.patch("/topics/{topic_id}", response_model=TopicResponse)
def editar_topic(
    topic_id: str,
    body: KnowledgeUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de um tópico."""
    topic = _get_or_404(db, topic_id, nivel=1)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(topic, field, value)
    db.commit()
    db.refresh(topic)
    subtopics = (
        db.query(Topico)
        .filter(Topico.parent_id == topic.id, Topico.nivel == 2, Topico.ativo == True)
        .all()
    )
    return TopicResponse(
        id=topic.id,
        nome=topic.nome,
        descricao=topic.descricao,
        peso_edital=topic.peso_edital,
        ativo=topic.ativo,
        subtopics=[
            SubtopicResponse(id=s.id, nome=s.nome, descricao=s.descricao, decay_rate=s.decay_rate, ativo=s.ativo)
            for s in subtopics
        ],
    )


@router.delete("/topics/{topic_id}", status_code=204)
def deletar_topic(
    topic_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: desativa um tópico (soft-delete). Rejeita se tiver subtópicos ativos."""
    topic = _get_or_404(db, topic_id, nivel=1)
    filhos_ativos = db.query(Topico).filter(
        Topico.parent_id == topic_id, Topico.ativo == True
    ).count()
    if filhos_ativos:
        raise HTTPException(
            status_code=400,
            detail=f"Impossivel desativar: topic possui {filhos_ativos} subtopico(s) ativo(s)",
        )
    topic.ativo = False
    db.commit()


# ─── Subtopics ────────────────────────────────────────────────────────────────

@router.post("/subtopics", response_model=SubtopicResponse, status_code=201)
def criar_subtopic(
    body: SubtopicCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cria um subtópico dentro de um topic."""
    topic = _get_or_404(db, body.topic_id, nivel=1)
    topico = Topico(
        id=str(uuid.uuid4()),
        nome=body.nome,
        nivel=2,
        parent_id=topic.id,
        area=topic.area,
        descricao=body.descricao,
        decay_rate=body.decay_rate,
        dependencias_json=body.dependencias_json,
        peso_edital=topic.peso_edital,
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return SubtopicResponse(
        id=topico.id,
        nome=topico.nome,
        descricao=topico.descricao,
        decay_rate=topico.decay_rate,
        ativo=topico.ativo,
    )


@router.patch("/subtopics/{subtopic_id}", response_model=SubtopicResponse)
def editar_subtopic(
    subtopic_id: str,
    body: KnowledgeUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de um subtópico."""
    subtopic = _get_or_404(db, subtopic_id, nivel=2)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(subtopic, field, value)
    db.commit()
    db.refresh(subtopic)
    return SubtopicResponse(
        id=subtopic.id,
        nome=subtopic.nome,
        descricao=subtopic.descricao,
        decay_rate=subtopic.decay_rate,
        ativo=subtopic.ativo,
    )


@router.delete("/subtopics/{subtopic_id}", status_code=204)
def deletar_subtopic(
    subtopic_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: desativa um subtópico (soft-delete)."""
    subtopic = _get_or_404(db, subtopic_id, nivel=2)
    subtopic.ativo = False
    db.commit()
