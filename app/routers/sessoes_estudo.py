"""
POST /sessoes-estudo  — registra sessão de estudo de teoria
GET  /sessoes-estudo  — histórico do aluno
"""
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.sessao_estudo import SessaoEstudo

router = APIRouter(prefix="/sessoes-estudo", tags=["sessoes-estudo"])


class SessaoEstudoRequest(BaseModel):
    subtopico_id: Optional[str] = None
    tipo: str = "teoria"  # "teoria" | "questoes"
    data: date
    duracao_min: Optional[int] = None


class SessaoEstudoResponse(BaseModel):
    id: str
    subtopico_id: Optional[str]
    tipo: str
    data: date
    duracao_min: Optional[int]

    class Config:
        from_attributes = True


@router.post("", response_model=SessaoEstudoResponse, status_code=201)
def registrar_sessao(
    body: SessaoEstudoRequest,
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    sessao = SessaoEstudo(
        id=str(uuid.uuid4()),
        aluno_id=aluno.id,
        subtopico_id=body.subtopico_id,
        tipo=body.tipo,
        data=body.data,
        duracao_min=body.duracao_min,
    )
    db.add(sessao)
    db.commit()
    db.refresh(sessao)
    return sessao


@router.get("", response_model=List[SessaoEstudoResponse])
def listar_sessoes(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    return (
        db.query(SessaoEstudo)
        .filter(SessaoEstudo.aluno_id == aluno.id)
        .order_by(SessaoEstudo.data.desc())
        .limit(limit)
        .all()
    )
