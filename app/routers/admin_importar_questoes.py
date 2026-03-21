import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ai_provider import get_ai_provider
from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.questao_banco import QuestaoBanco
from app.models.question_subtopic import QuestionSubtopic
from app.models.topico import Topico
from pydantic import ValidationError

from app.schemas.questao_banco import (
    ImportacaoRequest,
    ImportacaoResponse,
    QuestaoBancoResponse,
    QuestaoImportItem,
    QuestaoUpdateRequest,
)
from app.schemas.question_subtopic import AssociarSubtopicoRequest, SubtopicoInfo
from app.services.sugestao_subtopicos import salvar_sugestoes, sugerir_subtopicos

router = APIRouter(prefix="/admin", tags=["admin — importação de questões"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _gerar_question_code(disciplina: str, banca: str, ano: Optional[int], db: Session) -> str:
    """Gera código único no formato DISCIPLINA-BANCA-ANO-SEQUENCIAL."""
    banca_part = (banca or "SEM-BANCA").upper().replace(" ", "-")
    ano_part = str(ano) if ano else "SEM-ANO"
    prefix = f"{disciplina.upper()}-{banca_part}-{ano_part}"

    prefix_escaped = prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    count = db.query(QuestaoBanco).filter(
        QuestaoBanco.question_code.like(f"{prefix_escaped}-%", escape="\\")
    ).count()

    seq = str(count + 1).zfill(4)
    return f"{prefix}-{seq}"


def _subtopicos_da_questao(question_id: str, db: Session) -> List[SubtopicoInfo]:
    """Retorna os subtópicos associados a uma questão, incluindo a fonte (ia|manual)."""
    rows = (
        db.query(Topico, QuestionSubtopic.fonte)
        .join(QuestionSubtopic, QuestionSubtopic.subtopic_id == Topico.id)
        .filter(QuestionSubtopic.question_id == question_id)
        .all()
    )
    return [SubtopicoInfo(id=t.id, nome=t.nome, nivel=t.nivel, fonte=fonte) for t, fonte in rows]


def _questao_response(q: QuestaoBanco, db: Session) -> QuestaoBancoResponse:
    """Monta QuestaoBancoResponse com subtópicos populados."""
    data = QuestaoBancoResponse.model_validate(q)
    data.subtopicos = _subtopicos_da_questao(q.id, db)
    return data


# ─── Endpoints — importação ───────────────────────────────────────────────────

@router.post("/importar-questoes", response_model=ImportacaoResponse, status_code=201)
def importar_questoes(
    body: ImportacaoRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: importa questões em lote a partir de estrutura JSON/CSV pré-processada."""
    importadas = 0
    erros: list[str] = []
    questoes_importadas: list[QuestaoBanco] = []

    # Fase 1: salvar questões individualmente (commit por item para isolar falhas)
    for i, raw in enumerate(body.questoes, start=1):
        try:
            item = QuestaoImportItem.model_validate(raw)
            disciplina_sigla = item.materia.upper().replace(" ", "_")
            question_code = _gerar_question_code(
                disciplina_sigla, item.board or "", item.year, db
            )
            alts_json = json.dumps(
                item.alternatives.model_dump(exclude_none=False) if item.alternatives else {},
                ensure_ascii=False,
            )
            questao = QuestaoBanco(
                id=str(uuid.uuid4()),
                question_code=question_code,
                subject=item.subject,
                statement=item.statement,
                alternatives_json=alts_json,
                correct_answer=item.correct_answer,
                board=item.board,
                year=item.year,
            )
            db.add(questao)
            db.commit()
            questoes_importadas.append(questao)
            importadas += 1

        except ValidationError as exc:
            erros.append(f"Questão {i}: {exc.errors()[0]['msg']}")
        except Exception as exc:
            db.rollback()
            erros.append(f"Questão {i}: {str(exc)}")

    # Fase 2: classificação IA (best-effort, após commit das questões)
    avisos_ia: list[str] = []
    try:
        subtopicos_nivel2 = (
            db.query(Topico).filter(Topico.nivel == 2, Topico.ativo == True).all()
        )
        if subtopicos_nivel2 and questoes_importadas:
            ai = get_ai_provider()
            for questao in questoes_importadas:
                ids_sugeridos = sugerir_subtopicos(questao, subtopicos_nivel2, ai)
                if ids_sugeridos:
                    salvar_sugestoes(str(questao.id), ids_sugeridos, db)
                else:
                    avisos_ia.append(f"{questao.question_code}: sem classificação IA")
            db.commit()
    except Exception as exc:
        avisos_ia.append(f"Classificação IA falhou: {str(exc)}")

    return ImportacaoResponse(importadas=importadas, erros=erros, avisos_ia=avisos_ia)


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

    questoes = q.order_by(QuestaoBanco.created_at.desc()).all()
    return [_questao_response(questao, db) for questao in questoes]


# ─── Endpoints — subtópicos ───────────────────────────────────────────────────

@router.get("/questoes-banco/{question_id}/subtopicos", response_model=List[SubtopicoInfo])
def listar_subtopicos_questao(
    question_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista os subtópicos associados a uma questão."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    return _subtopicos_da_questao(question_id, db)


@router.post("/questoes-banco/{question_id}/subtopicos", response_model=List[SubtopicoInfo])
def associar_subtopicos(
    question_id: str,
    body: AssociarSubtopicoRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: associa um ou mais subtópicos a uma questão (ignora duplicatas)."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    for subtopic_id in body.subtopic_ids:
        topico = db.query(Topico).filter(Topico.id == subtopic_id, Topico.nivel == 2).first()
        if not topico:
            raise HTTPException(
                status_code=422,
                detail=f"subtopic_id '{subtopic_id}' não encontrado ou não é um subtópico (nivel=2)",
            )

        assoc = QuestionSubtopic(
            id=str(uuid.uuid4()),
            question_id=question_id,
            subtopic_id=subtopic_id,
            fonte="manual",
        )
        db.add(assoc)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()  # ignora duplicata silenciosamente

    db.commit()
    return _subtopicos_da_questao(question_id, db)


@router.delete(
    "/questoes-banco/{question_id}/subtopicos/{subtopic_id}",
    status_code=204,
    response_class=Response,
)
def remover_subtopico(
    question_id: str,
    subtopic_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: remove a associação entre uma questão e um subtópico."""
    assoc = (
        db.query(QuestionSubtopic)
        .filter(
            QuestionSubtopic.question_id == question_id,
            QuestionSubtopic.subtopic_id == subtopic_id,
        )
        .first()
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="Associação não encontrada")

    db.delete(assoc)
    db.commit()


# ─── Endpoints — CRUD de questões ────────────────────────────────────────────

@router.get("/questoes", response_model=List[QuestaoBancoResponse])
def listar_questoes(
    materia: Optional[str] = Query(None, description="Filtra por subject (matéria)"),
    subtopico: Optional[str] = Query(None, description="Filtra por nome de subtópico associado"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista questões com filtros por matéria e subtópico, paginado."""
    q = db.query(QuestaoBanco)

    if materia:
        q = q.filter(QuestaoBanco.subject.ilike(f"%{materia}%"))

    if subtopico:
        q = (
            q.join(QuestionSubtopic, QuestionSubtopic.question_id == QuestaoBanco.id)
            .join(Topico, Topico.id == QuestionSubtopic.subtopic_id)
            .filter(Topico.nome.ilike(f"%{subtopico}%"))
        )

    questoes = (
        q.order_by(QuestaoBanco.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return [_questao_response(questao, db) for questao in questoes]


@router.patch("/questoes/{question_id}", response_model=QuestaoBancoResponse)
def editar_questao(
    question_id: str,
    body: QuestaoUpdateRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de uma questão do banco."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    if body.subject is not None:
        questao.subject = body.subject
    if body.statement is not None:
        questao.statement = body.statement
    if body.alternatives is not None:
        questao.alternatives_json = json.dumps(body.alternatives.model_dump(), ensure_ascii=False)
    if body.correct_answer is not None:
        questao.correct_answer = body.correct_answer
    if body.board is not None:
        questao.board = body.board
    if body.year is not None:
        questao.year = body.year

    db.commit()
    db.refresh(questao)
    return _questao_response(questao, db)


@router.delete("/questoes/{question_id}", status_code=204, response_class=Response)
def deletar_questao(
    question_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: deleta uma questão do banco (remove associações de subtópicos antes)."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    db.query(QuestionSubtopic).filter(QuestionSubtopic.question_id == question_id).delete()
    db.delete(questao)
    db.commit()


@router.post("/questoes/{question_id}/sugerir-subtopico", response_model=List[SubtopicoInfo])
def sugerir_subtopico_questao(
    question_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: sugere subtópicos para uma questão via IA. Retorna sugestões sem salvar — admin confirma."""
    questao = db.query(QuestaoBanco).filter(QuestaoBanco.id == question_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    subtopicos = db.query(Topico).filter(Topico.nivel == 2, Topico.ativo == True).all()
    if not subtopicos:
        raise HTTPException(status_code=422, detail="Nenhum subtópico cadastrado no banco")

    ai = get_ai_provider()
    ids_sugeridos = sugerir_subtopicos(questao, subtopicos, ai)

    id_set = set(ids_sugeridos)
    sugeridos = [
        SubtopicoInfo(id=t.id, nome=t.nome, nivel=t.nivel, fonte="ia")
        for t in subtopicos
        if t.id in id_set
    ]
    return sugeridos
