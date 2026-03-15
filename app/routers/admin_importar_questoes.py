import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.questao_banco import QuestaoBanco
from app.schemas.questao_banco import (
    ImportacaoRequest,
    ImportacaoResponse,
    QuestaoBancoResponse,
)

router = APIRouter(prefix="/admin", tags=["admin — importação de questões"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _gerar_question_code(disciplina: str, banca: str, ano: Optional[int], db: Session) -> str:
    """Gera código único no formato DISCIPLINA-BANCA-ANO-SEQUENCIAL."""
    banca_part = (banca or "SEM-BANCA").upper().replace(" ", "-")
    ano_part = str(ano) if ano else "SEM-ANO"
    prefix = f"{disciplina.upper()}-{banca_part}-{ano_part}"

    count = db.query(QuestaoBanco).filter(
        QuestaoBanco.question_code.like(f"{prefix}-%")
    ).count()

    seq = str(count + 1).zfill(4)
    return f"{prefix}-{seq}"


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/importar-questoes", response_model=ImportacaoResponse, status_code=201)
def importar_questoes(
    body: ImportacaoRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: importa questões em lote a partir de estrutura JSON/CSV pré-processada."""
    importadas = 0
    erros: list[str] = []

    for i, item in enumerate(body.questoes, start=1):
        try:
            question_code = _gerar_question_code(
                body.disciplina_sigla, item.board or "", item.year, db
            )

            questao = QuestaoBanco(
                id=str(uuid.uuid4()),
                question_code=question_code,
                subject=item.subject,
                statement=item.statement,
                alternatives_json=json.dumps(item.alternatives.model_dump(), ensure_ascii=False),
                correct_answer=item.correct_answer,
                board=item.board,
                year=item.year,
            )
            db.add(questao)
            db.flush()  # garante que o question_code único é resolvido antes da próxima iteração
            importadas += 1

        except Exception as exc:
            erros.append(f"Questão {i}: {str(exc)}")

    db.commit()
    return ImportacaoResponse(importadas=importadas, erros=erros)


@router.get("/questoes-banco", response_model=List[QuestaoBancoResponse])
def listar_questoes_banco(
    subject: Optional[str] = Query(None),
    board: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    disciplina_sigla: Optional[str] = Query(None, description="Filtra pelo prefixo do question_code"),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista questões importadas com filtros opcionais."""
    q = db.query(QuestaoBanco)

    if subject:
        q = q.filter(QuestaoBanco.subject.ilike(f"%{subject}%"))
    if board:
        q = q.filter(QuestaoBanco.board.ilike(f"%{board}%"))
    if year:
        q = q.filter(QuestaoBanco.year == year)
    if disciplina_sigla:
        q = q.filter(QuestaoBanco.question_code.like(f"{disciplina_sigla.upper()}-%"))

    return q.order_by(QuestaoBanco.created_at.desc()).all()
