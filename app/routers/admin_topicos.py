import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.question_subtopic import QuestionSubtopic
from app.models.topico import Topico
from app.schemas.topico import TopicoCreate, TopicoResponse, TopicoUpdate

router = APIRouter(prefix="/admin/topicos", tags=["admin - tópicos"])


@router.post("", response_model=TopicoResponse, status_code=201)
def criar_topico(
    body: TopicoCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cria matéria (nivel=0), bloco (nivel=1) ou tópico (nivel=2)."""
    if body.parent_id:
        parent = db.query(Topico).filter(Topico.id == body.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Tópico pai não encontrado")

    topico = Topico(
        id=str(uuid.uuid4()),
        nome=body.nome,
        nivel=body.nivel,
        parent_id=body.parent_id,
        descricao=body.descricao,
        area=body.area,
        banca=body.banca,
        peso_edital=body.peso_edital,
        decay_rate=body.decay_rate,
        dependencias_json=body.dependencias_json,
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return topico


@router.get("", response_model=List[TopicoResponse])
def listar_topicos(
    nivel: Optional[int] = Query(None, description="Filtrar por nível: 0=matéria, 1=bloco, 2=tópico"),
    area: Optional[str] = Query(None),
    banca: Optional[str] = Query(None),
    parent_id: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista tópicos com filtros opcionais."""
    q = db.query(Topico)
    if apenas_ativos:
        q = q.filter(Topico.ativo == True)
    if nivel is not None:
        q = q.filter(Topico.nivel == nivel)
    if area:
        q = q.filter(Topico.area == area)
    if banca:
        q = q.filter(Topico.banca == banca)
    if parent_id:
        q = q.filter(Topico.parent_id == parent_id)
    return q.order_by(Topico.nivel, Topico.nome).all()


@router.get("/questoes-por-subtopico", response_model=Dict[str, int])
def questoes_por_subtopico(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: retorna contagem de questões por subtópico {subtopic_id: count}."""
    rows = (
        db.query(QuestionSubtopic.subtopic_id, func.count(QuestionSubtopic.question_id))
        .group_by(QuestionSubtopic.subtopic_id)
        .all()
    )
    return {row[0]: row[1] for row in rows}


@router.get("/{topico_id}", response_model=TopicoResponse)
def detalhe_topico(
    topico_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: retorna detalhes de um tópico."""
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")
    return topico


@router.patch("/{topico_id}", response_model=TopicoResponse)
def editar_topico(
    topico_id: str,
    body: TopicoUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de um tópico."""
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(topico, field, value)

    db.commit()
    db.refresh(topico)
    return topico


@router.delete("/{topico_id}", status_code=204)
def desativar_topico(
    topico_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: desativa um tópico (soft-delete). Não remove do banco."""
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")

    topico.ativo = False
    db.commit()
