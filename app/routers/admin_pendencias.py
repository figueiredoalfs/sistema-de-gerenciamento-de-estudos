"""
app/routers/admin_pendencias.py — Validação de matérias e bancas não reconhecidas.
"""
import uuid
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.banca import Banca
from app.models.questao_banco import QuestaoBanco
from app.models.topico import Topico
from app.routers.admin_importar_questoes import _questao_response, _calcular_pendente
from app.schemas.questao_banco import QuestaoBancoResponse

router = APIRouter(prefix="/admin", tags=["admin — pendências"])


class ResolverMateriaRequest(BaseModel):
    acao: Literal["vincular", "criar"]
    topico_id: Optional[str] = None    # obrigatório se acao="vincular"
    nova_materia: Optional[str] = None  # obrigatório se acao="criar"


class ResolverBancaRequest(BaseModel):
    acao: Literal["vincular", "criar"]
    banca_id: Optional[str] = None    # obrigatório se acao="vincular"
    nova_banca: Optional[str] = None   # obrigatório se acao="criar"


def _set_pendente(questao: QuestaoBanco, db: Session) -> None:
    """Atualiza materia_pendente com base no estado atual da questão."""
    questao.materia_pendente = _calcular_pendente(questao.materia or "", questao.board or "", db)


@router.get("/materias-pendentes", response_model=List[QuestaoBancoResponse])
def listar_materias_pendentes(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista questões cujas matérias ou bancas precisam de validação."""
    questoes = (
        db.query(QuestaoBanco)
        .filter(QuestaoBanco.materia_pendente == True)
        .order_by(QuestaoBanco.created_at.desc())
        .all()
    )
    return [_questao_response(q, db) for q in questoes]


@router.post("/materias-pendentes/{question_id}/resolver-materia", response_model=QuestaoBancoResponse)
def resolver_materia(
    question_id: str,
    body: ResolverMateriaRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: resolve a matéria pendente — vincula a existente ou cria nova."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    if body.acao == "vincular":
        if not body.topico_id:
            raise HTTPException(status_code=422, detail="topico_id obrigatório para acao='vincular'")
        topico = db.query(Topico).filter(Topico.id == body.topico_id, Topico.nivel == 0).first()
        if not topico:
            raise HTTPException(status_code=404, detail="Matéria não encontrada")
        questao.materia = topico.nome
        questao.subject = topico.nome

    elif body.acao == "criar":
        nome = (body.nova_materia or questao.materia or "").strip()
        if not nome:
            raise HTTPException(status_code=422, detail="nova_materia obrigatório para acao='criar'")
        existente = db.query(Topico).filter(Topico.nivel == 0, Topico.nome.ilike(nome)).first()
        if not existente:
            db.add(Topico(id=str(uuid.uuid4()), nivel=0, nome=nome, ativo=True))
        questao.materia = nome
        questao.subject = nome

    # Regenera o question_code com a nova matéria
    from app.routers.admin_importar_questoes import _gerar_question_code
    disciplina_sigla = (questao.materia or "SEM-DISCIPLINA").upper().replace(" ", "_")
    questao.question_code = _gerar_question_code(disciplina_sigla, questao.board or "", questao.year, db)

    _set_pendente(questao, db)
    db.commit()
    db.refresh(questao)
    return _questao_response(questao, db)


@router.post("/materias-pendentes/{question_id}/resolver-banca", response_model=QuestaoBancoResponse)
def resolver_banca(
    question_id: str,
    body: ResolverBancaRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: resolve a banca pendente — vincula a existente ou cria nova."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    if body.acao == "vincular":
        if not body.banca_id:
            raise HTTPException(status_code=422, detail="banca_id obrigatório para acao='vincular'")
        banca = db.query(Banca).filter(Banca.id == body.banca_id, Banca.ativo == True).first()
        if not banca:
            raise HTTPException(status_code=404, detail="Banca não encontrada")
        questao.board = banca.nome

    elif body.acao == "criar":
        nome = (body.nova_banca or questao.board or "").strip()
        if not nome:
            raise HTTPException(status_code=422, detail="nova_banca obrigatório para acao='criar'")
        existente = db.query(Banca).filter(Banca.nome.ilike(nome)).first()
        if not existente:
            db.add(Banca(id=str(uuid.uuid4()), nome=nome, ativo=True))
        questao.board = nome

    # Regenera o question_code com a nova banca
    from app.routers.admin_importar_questoes import _gerar_question_code
    disciplina_sigla = (questao.materia or "SEM-DISCIPLINA").upper().replace(" ", "_")
    questao.question_code = _gerar_question_code(disciplina_sigla, questao.board or "", questao.year, db)

    _set_pendente(questao, db)
    db.commit()
    db.refresh(questao)
    return _questao_response(questao, db)
