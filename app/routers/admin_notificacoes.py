"""
admin_notificacoes.py — CRUD de notificações administrativas.

GET    /admin/notificacoes          — lista notificações (suporta ?lida=false)
POST   /admin/notificacoes          — cria nova notificação
PATCH  /admin/notificacoes/{id}/marcar-lida — marca como lida
DELETE /admin/notificacoes/{id}     — remove
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.notificacao import Notificacao

router = APIRouter(prefix="/admin/notificacoes", tags=["admin — notificações"])


class NotificacaoCreate(BaseModel):
    titulo: str
    mensagem: str
    tipo: str = "info"


class NotificacaoResponse(BaseModel):
    id: str
    titulo: str
    mensagem: str
    tipo: str
    lida: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=List[NotificacaoResponse])
def listar(
    lida: Optional[bool] = Query(None, description="Filtrar por status de leitura"),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    q = db.query(Notificacao)
    if lida is not None:
        q = q.filter(Notificacao.lida == lida)
    return q.order_by(Notificacao.created_at.desc()).all()


@router.post("", response_model=NotificacaoResponse, status_code=201)
def criar(
    body: NotificacaoCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    n = Notificacao(
        id=str(uuid.uuid4()),
        titulo=body.titulo,
        mensagem=body.mensagem,
        tipo=body.tipo,
        lida=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


@router.patch("/{notificacao_id}/marcar-lida", response_model=NotificacaoResponse)
def marcar_lida(
    notificacao_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    n = db.query(Notificacao).filter(Notificacao.id == notificacao_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    n.lida = True
    db.commit()
    db.refresh(n)
    return n


@router.delete("/{notificacao_id}", status_code=204, response_class=Response)
def deletar(
    notificacao_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    n = db.query(Notificacao).filter(Notificacao.id == notificacao_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    db.delete(n)
    db.commit()
