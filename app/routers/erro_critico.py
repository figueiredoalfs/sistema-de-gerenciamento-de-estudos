"""
Endpoints de erros críticos.

POST  /erro-critico              — registrar erro critico
GET   /erros-criticos            — listar com filtro por status
PATCH /erro-critico/{id}/status  — atualizar status
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.erro_critico import ErroCritico
from app.schemas.erro_critico import (
    ErroCriticoListResponse,
    ErroCriticoOut,
    ErroCriticoRequest,
    ErroCriticoStatusUpdate,
)

router = APIRouter(tags=["erros-criticos"])

STATUS_VALIDOS = {"pendente", "em_revisao", "resolvido"}


@router.post("/erro-critico", response_model=ErroCriticoOut, status_code=201)
def registrar_erro(
    body: ErroCriticoRequest,
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    """Registra um erro crítico. status='pendente' por padrão."""
    erro = ErroCritico(
        aluno_id=aluno.id,
        topico_id=body.topico_id,
        id_bateria=body.id_bateria,
        materia=body.materia,
        topico_texto=body.topico_texto,
        qtd_erros=body.qtd_erros,
        observacao=body.observacao,
        status="pendente",
    )
    db.add(erro)
    db.commit()
    db.refresh(erro)
    return ErroCriticoOut.model_validate(erro)


@router.get("/erros-criticos", response_model=ErroCriticoListResponse)
def listar_erros(
    status: str = Query(None, description="pendente | em_revisao | resolvido"),
    materia: str = Query(None),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    """Lista erros críticos do aluno com filtros opcionais."""
    q = db.query(ErroCritico).filter(ErroCritico.aluno_id == aluno.id)

    if status and status in STATUS_VALIDOS:
        q = q.filter(ErroCritico.status == status)
    if materia:
        q = q.filter(ErroCritico.materia.ilike(f"%{materia}%"))

    total = q.count()
    itens = (
        q.order_by(ErroCritico.data.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
        .all()
    )

    return ErroCriticoListResponse(
        total=total,
        itens=[ErroCriticoOut.model_validate(e) for e in itens],
    )


@router.patch("/erro-critico/{erro_id}/status", response_model=ErroCriticoOut)
def atualizar_status(
    erro_id: str,
    body: ErroCriticoStatusUpdate,
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    """Atualiza o status de um erro crítico."""
    if body.status not in STATUS_VALIDOS:
        raise HTTPException(400, detail=f"Status inválido. Use: {STATUS_VALIDOS}")

    erro = db.query(ErroCritico).filter(
        ErroCritico.id == erro_id,
        ErroCritico.aluno_id == aluno.id,
    ).first()

    if not erro:
        raise HTTPException(404, detail="Erro crítico não encontrado.")

    erro.status = body.status
    db.commit()
    db.refresh(erro)
    return ErroCriticoOut.model_validate(erro)
