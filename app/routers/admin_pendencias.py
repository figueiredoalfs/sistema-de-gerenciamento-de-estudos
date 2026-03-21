"""
app/routers/admin_pendencias.py — Validação de matérias novas importadas.
"""
import uuid
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.questao_banco import QuestaoBanco
from app.models.topico import Topico
from app.routers.admin_importar_questoes import _questao_response
from app.schemas.questao_banco import QuestaoBancoResponse

router = APIRouter(prefix="/admin", tags=["admin — pendências"])


class ResolverPendenciaRequest(BaseModel):
    acao: Literal["vincular", "criar"]
    topico_id: Optional[str] = None    # obrigatório se acao="vincular"
    nova_materia: Optional[str] = None  # obrigatório se acao="criar"


@router.get("/materias-pendentes", response_model=List[QuestaoBancoResponse])
def listar_materias_pendentes(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista questões cujas matérias precisam de validação."""
    questoes = (
        db.query(QuestaoBanco)
        .filter(QuestaoBanco.materia_pendente == True)
        .order_by(QuestaoBanco.created_at.desc())
        .all()
    )
    return [_questao_response(q, db) for q in questoes]


@router.post("/materias-pendentes/{question_id}/resolver", response_model=QuestaoBancoResponse)
def resolver_pendencia(
    question_id: str,
    body: ResolverPendenciaRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: resolve uma matéria pendente — vincula a existente ou cria nova."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    if body.acao == "vincular":
        if not body.topico_id:
            raise HTTPException(status_code=422, detail="topico_id obrigatório para acao='vincular'")
        topico = db.query(Topico).filter(Topico.id == body.topico_id, Topico.nivel == 0).first()
        if not topico:
            raise HTTPException(status_code=404, detail="Matéria não encontrada")
        questao.subject = topico.nome

    elif body.acao == "criar":
        nome = (body.nova_materia or questao.subject).strip()
        if not nome:
            raise HTTPException(status_code=422, detail="nova_materia obrigatório para acao='criar'")
        # Verifica se já existe (corrida ou digitação duplicada)
        existente = db.query(Topico).filter(
            Topico.nivel == 0, Topico.nome.ilike(nome)
        ).first()
        if not existente:
            db.add(Topico(
                id=str(uuid.uuid4()),
                nivel=0,
                nome=nome,
                ativo=True,
            ))
        questao.subject = nome

    questao.materia_pendente = False
    db.commit()
    db.refresh(questao)
    return _questao_response(questao, db)
