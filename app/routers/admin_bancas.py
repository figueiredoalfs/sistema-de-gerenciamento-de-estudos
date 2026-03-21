"""
app/routers/admin_bancas.py — Gestão de bancas examinadoras.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.banca import Banca

router = APIRouter(prefix="/admin/bancas", tags=["admin — bancas"])


class BancaCreate(BaseModel):
    nome: str


class BancaUpdate(BaseModel):
    nome: Optional[str] = None
    ativo: Optional[bool] = None


class BancaResponse(BaseModel):
    id: str
    nome: str
    ativo: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=List[BancaResponse])
def listar_bancas(
    apenas_ativas: bool = True,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista bancas cadastradas."""
    q = db.query(Banca)
    if apenas_ativas:
        q = q.filter(Banca.ativo == True)
    return q.order_by(Banca.nome).all()


@router.post("", response_model=BancaResponse, status_code=201)
def criar_banca(
    body: BancaCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cadastra nova banca."""
    nome = body.nome.strip()
    if not nome:
        raise HTTPException(status_code=422, detail="Nome da banca é obrigatório")
    existente = db.query(Banca).filter(Banca.nome.ilike(nome)).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"Banca '{nome}' já existe")
    banca = Banca(id=str(uuid.uuid4()), nome=nome, ativo=True)
    db.add(banca)
    db.commit()
    db.refresh(banca)
    # Reclassifica questões que possam ter essa banca e estavam pendentes
    from app.scripts.reclassificar_pendencias import reclassificar
    reclassificar(db)
    return banca


@router.patch("/{banca_id}", response_model=BancaResponse)
def editar_banca(
    banca_id: str,
    body: BancaUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita nome ou status de uma banca."""
    banca = db.query(Banca).filter(Banca.id == banca_id).first()
    if not banca:
        raise HTTPException(status_code=404, detail="Banca não encontrada")
    if body.nome is not None:
        banca.nome = body.nome.strip()
    if body.ativo is not None:
        banca.ativo = body.ativo
    db.commit()
    db.refresh(banca)
    return banca


@router.delete("/{banca_id}", status_code=204, response_class=Response)
def desativar_banca(
    banca_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: desativa uma banca (soft-delete)."""
    banca = db.query(Banca).filter(Banca.id == banca_id).first()
    if not banca:
        raise HTTPException(status_code=404, detail="Banca não encontrada")
    banca.ativo = False
    db.commit()
