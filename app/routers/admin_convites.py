"""
admin_convites.py — Gerenciamento de códigos de convite.

GET    /admin/convites       — lista todos os códigos
POST   /admin/convites       — cria novo código
PATCH  /admin/convites/{id}  — ativa/desativa
DELETE /admin/convites/{id}  — remove
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.codigo_convite import CodigoConvite

router = APIRouter(prefix="/admin/convites", tags=["admin — convites"])


class ConviteResponse(BaseModel):
    id: str
    codigo: str
    descricao: Optional[str] = None
    usos_maximos: Optional[int] = None
    usos_atuais: int
    ativo: bool
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConviteCreate(BaseModel):
    codigo: str
    descricao: Optional[str] = None
    usos_maximos: Optional[int] = None
    expires_at: Optional[datetime] = None


class ConvitePatch(BaseModel):
    ativo: bool


@router.get("", response_model=List[ConviteResponse])
def listar_convites(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    return db.query(CodigoConvite).order_by(CodigoConvite.created_at.desc()).all()


@router.post("", response_model=ConviteResponse, status_code=201)
def criar_convite(
    body: ConviteCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    codigo_upper = body.codigo.strip().upper()
    if db.query(CodigoConvite).filter(CodigoConvite.codigo == codigo_upper).first():
        raise HTTPException(status_code=400, detail="Código já existe")
    convite = CodigoConvite(
        id=str(uuid.uuid4()),
        codigo=codigo_upper,
        descricao=body.descricao,
        usos_maximos=body.usos_maximos,
        expires_at=body.expires_at,
    )
    db.add(convite)
    db.commit()
    db.refresh(convite)
    return convite


@router.patch("/{convite_id}", response_model=ConviteResponse)
def toggle_convite(
    convite_id: str,
    body: ConvitePatch,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    convite = db.query(CodigoConvite).filter(CodigoConvite.id == convite_id).first()
    if not convite:
        raise HTTPException(status_code=404, detail="Código não encontrado")
    convite.ativo = body.ativo
    db.commit()
    db.refresh(convite)
    return convite


@router.delete("/{convite_id}", status_code=204)
def deletar_convite(
    convite_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    convite = db.query(CodigoConvite).filter(CodigoConvite.id == convite_id).first()
    if not convite:
        raise HTTPException(status_code=404, detail="Código não encontrado")
    db.delete(convite)
    db.commit()
