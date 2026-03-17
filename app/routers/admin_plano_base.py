"""
admin_plano_base.py — CRUD e geração via IA de PlanoBase.

GET    /admin/planos-base           — lista planos
POST   /admin/planos-base/gerar     — gera novo plano via IA
POST   /admin/planos-base           — cria plano manual
GET    /admin/planos-base/{id}      — detalhe
PATCH  /admin/planos-base/{id}      — edita / aprova
DELETE /admin/planos-base/{id}      — remove
"""
import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.ai_provider import get_ai_provider
from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.plano_base import PlanoBase
from app.schemas.plano_base import (
    GerarPlanoRequest,
    PlanoBaseCreate,
    PlanoBaseResponse,
    PlanoBaseUpdate,
)
from app.models.perfil_estudo import PerfilEstudo
from app.services.avancar_fase import associar_plano_base, verificar_e_avancar
from app.services.gerar_plano_base import gerar_plano_via_ia

router = APIRouter(prefix="/admin/planos-base", tags=["admin — planos base"])


def _to_response(p: PlanoBase) -> PlanoBaseResponse:
    return PlanoBaseResponse.model_validate(p)


@router.get("", response_model=List[PlanoBaseResponse])
def listar_planos(
    area: Optional[str] = Query(None),
    perfil: Optional[str] = Query(None),
    pendente_revisao: bool = Query(False, description="Filtrar apenas planos gerados por IA não revisados"),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    q = db.query(PlanoBase)
    if area:
        q = q.filter(PlanoBase.area == area)
    if perfil:
        q = q.filter(PlanoBase.perfil == perfil)
    if pendente_revisao:
        q = q.filter(PlanoBase.gerado_por_ia == True, PlanoBase.revisado_admin == False)  # noqa: E712
    return [_to_response(p) for p in q.order_by(PlanoBase.created_at.desc()).all()]


@router.post("/gerar", response_model=PlanoBaseResponse, status_code=201)
def gerar_plano(
    body: GerarPlanoRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Gera um PlanoBase via IA e salva no banco sem revisão."""
    ai = get_ai_provider()
    fases = gerar_plano_via_ia(body.area, body.perfil, ai)
    if not fases:
        raise HTTPException(status_code=422, detail="A IA não retornou fases válidas. Tente novamente.")

    plano = PlanoBase(
        id=str(uuid.uuid4()),
        area=body.area,
        perfil=body.perfil,
        gerado_por_ia=True,
        revisado_admin=False,
        fases_json=json.dumps(fases, ensure_ascii=False),
    )
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return _to_response(plano)


@router.post("", response_model=PlanoBaseResponse, status_code=201)
def criar_plano(
    body: PlanoBaseCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Cria um PlanoBase manualmente (já considerado revisado)."""
    fases = [f.model_dump() for f in body.fases]
    plano = PlanoBase(
        id=str(uuid.uuid4()),
        area=body.area,
        perfil=body.perfil,
        gerado_por_ia=False,
        revisado_admin=True,
        fases_json=json.dumps(fases, ensure_ascii=False),
    )
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return _to_response(plano)


@router.get("/{plano_id}", response_model=PlanoBaseResponse)
def detalhe_plano(
    plano_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    plano = db.query(PlanoBase).filter(PlanoBase.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return _to_response(plano)


@router.patch("/{plano_id}", response_model=PlanoBaseResponse)
def atualizar_plano(
    plano_id: str,
    body: PlanoBaseUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    plano = db.query(PlanoBase).filter(PlanoBase.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    if body.fases is not None:
        plano.fases_json = json.dumps([f.model_dump() for f in body.fases], ensure_ascii=False)
    if body.revisado_admin is not None:
        plano.revisado_admin = body.revisado_admin
    if body.ativo is not None:
        plano.ativo = body.ativo

    db.commit()
    db.refresh(plano)
    return _to_response(plano)


@router.post("/associar/{aluno_id}")
def associar_plano_ao_aluno(
    aluno_id: str,
    plano_id: str = Query(..., description="ID do PlanoBase a associar"),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: associa um PlanoBase ao aluno e redefine para fase 1."""
    plano = db.query(PlanoBase).filter(PlanoBase.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    ok = associar_plano_base(aluno_id, plano_id, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Perfil de estudo do aluno não encontrado")
    return {"ok": True, "plano_base_id": plano_id, "fase_atual": 1}


@router.post("/verificar-avanco/{aluno_id}")
def verificar_avanco(
    aluno_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: verifica e executa o avanço de fase do aluno se critérios forem atendidos."""
    return verificar_e_avancar(aluno_id, db)


@router.delete("/{plano_id}", status_code=204, response_class=Response)
def deletar_plano(
    plano_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    plano = db.query(PlanoBase).filter(PlanoBase.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    db.delete(plano)
    db.commit()
