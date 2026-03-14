"""
admin_ciclos.py — CRUD de ciclos de matérias por área.

GET    /admin/ciclos?area=fiscal   — lista matérias do ciclo (ordenadas por `ordem`)
POST   /admin/ciclos               — adiciona matéria ao ciclo
PATCH  /admin/ciclos/{id}          — atualiza ordem e/ou ativo
DELETE /admin/ciclos/{id}          — remove matéria do ciclo
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.ciclo_materia import CicloMateria
from app.models.topico import Topico
from app.schemas.ciclo_materia import (
    CicloMateriaCreate,
    CicloMateriaListResponse,
    CicloMateriaResponse,
    CicloMateriaUpdate,
)

router = APIRouter(prefix="/admin/ciclos", tags=["admin - ciclos"])


def _to_response(ciclo: CicloMateria) -> CicloMateriaResponse:
    return CicloMateriaResponse(
        id=ciclo.id,
        area=ciclo.area,
        subject_id=ciclo.subject_id,
        subject_nome=ciclo.subject.nome if ciclo.subject else None,
        ordem=ciclo.ordem,
        ativo=ciclo.ativo,
    )


@router.get("", response_model=CicloMateriaListResponse)
def listar_ciclo(
    area: str = Query(..., description="Área do concurso: fiscal, juridica, policial..."),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Lista todas as matérias do ciclo de uma área, ordenadas por `ordem`."""
    itens = (
        db.query(CicloMateria)
        .filter(CicloMateria.area == area)
        .order_by(CicloMateria.ordem)
        .all()
    )
    return CicloMateriaListResponse(
        area=area,
        total=len(itens),
        itens=[_to_response(c) for c in itens],
    )


@router.post("", response_model=CicloMateriaResponse, status_code=201)
def adicionar_ao_ciclo(
    body: CicloMateriaCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Adiciona uma matéria (Topico nivel=0) ao ciclo de uma área."""
    subject = db.query(Topico).filter(
        Topico.id == body.subject_id,
        Topico.nivel == 0,
        Topico.ativo == True,
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Matéria (nivel=0) não encontrada ou inativa")

    existente = db.query(CicloMateria).filter(
        CicloMateria.area == body.area,
        CicloMateria.subject_id == body.subject_id,
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Matéria já está no ciclo desta área")

    ciclo = CicloMateria(
        id=str(uuid.uuid4()),
        area=body.area,
        subject_id=body.subject_id,
        ordem=body.ordem,
    )
    db.add(ciclo)
    db.commit()
    db.refresh(ciclo)
    return _to_response(ciclo)


@router.patch("/{ciclo_id}", response_model=CicloMateriaResponse)
def atualizar_ciclo(
    ciclo_id: str,
    body: CicloMateriaUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Atualiza ordem e/ou status ativo de uma entrada do ciclo."""
    ciclo = db.query(CicloMateria).filter(CicloMateria.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=404, detail="Entrada do ciclo não encontrada")

    if body.ordem is not None:
        ciclo.ordem = body.ordem
    if body.ativo is not None:
        ciclo.ativo = body.ativo
    ciclo.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ciclo)
    return _to_response(ciclo)


@router.delete("/{ciclo_id}", status_code=204)
def remover_do_ciclo(
    ciclo_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Remove uma matéria do ciclo."""
    ciclo = db.query(CicloMateria).filter(CicloMateria.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=404, detail="Entrada do ciclo não encontrada")
    db.delete(ciclo)
    db.commit()
