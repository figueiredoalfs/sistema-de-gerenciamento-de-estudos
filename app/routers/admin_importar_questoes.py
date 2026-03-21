import json
import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from google import genai
from google.genai import types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
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

    # Fase 2: classificação IA (best-effort, apenas se solicitado)
    avisos_ia: list[str] = []
    if body.classificar_ia:
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


# ─── Endpoint — TEC Concursos (sem IA) ───────────────────────────────────────

@router.post("/importar-questoes-tec", response_model=dict)
async def importar_questoes_tec(
    file: UploadFile = File(...),
    _: Aluno = Depends(require_admin),
):
    """
    Admin: parseia PDF do TEC Concursos sem IA.
    Retorna preview das questões para o admin confirmar antes de salvar.
    PDF deve ser gerado pelo botão Imprimir do TEC Concursos via navegador.
    NÃO usar Print to PDF do Windows.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Envie um arquivo .pdf")

    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=422, detail="Arquivo PDF vazio")

    from app.services.tec_parser import parse_pdf_tec
    resultado = parse_pdf_tec(pdf_bytes)

    if resultado["erro"]:
        raise HTTPException(status_code=422, detail=resultado["erro"])

    return resultado


# ─── Endpoint — extração de PDF via IA ───────────────────────────────────────

_PROMPT_PDF = (
    "Você é um especialista em extração de questões de concursos públicos brasileiros.\n"
    "Analise este PDF e extraia TODAS as questões encontradas.\n\n"
    "Para cada questão, retorne um objeto JSON com:\n"
    '- "materia": disciplina (ex: "Direito Administrativo", "Português", "Matemática")\n'
    '- "subject": assunto específico (ex: "Atos Administrativos", "Concordância Verbal")\n'
    '- "statement": enunciado completo da questão\n'
    '- "alternatives": objeto com chaves A, B, C, D, E (use null se for questão Certo/Errado)\n'
    '- "correct_answer": gabarito ("A", "B", "C", "D", "E", "CERTO" ou "ERRADO")\n'
    '- "board": banca examinadora se mencionada, ou null\n'
    '- "year": ano da prova como número inteiro se mencionado, ou null\n\n'
    "Retorne SOMENTE um array JSON válido, sem texto adicional, sem markdown.\n"
    'Exemplo: [{"materia":"Direito Constitucional","subject":"Direitos Fundamentais",'
    '"statement":"...","alternatives":{"A":"...","B":"...","C":"...","D":"...","E":"..."},'
    '"correct_answer":"A","board":"CESPE","year":2023}]\n\n'
    "Se não encontrar questões, retorne []."
)


@router.post("/importar-questoes-pdf", response_model=List[Any])
async def extrair_questoes_pdf(
    file: UploadFile = File(...),
    _: Aluno = Depends(require_admin),
):
    """Admin: extrai questões de um PDF via Gemini Flash. Retorna preview sem salvar."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Envie um arquivo .pdf")

    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY não configurada")

    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=422, detail="Arquivo PDF vazio")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                types.Part(text=_PROMPT_PDF),
            ],
            config=types.GenerateContentConfig(
                max_output_tokens=65536,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        raw = response.text.strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erro na IA: {str(exc)}")

    # Remove markdown code fences se presentes
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        inicio = raw.find("[")
        fim = raw.rfind("]") + 1
        if inicio == -1 or fim == 0:
            raise HTTPException(status_code=502, detail=f"IA não retornou JSON válido. Resposta: {raw[:500]!r}")
        questoes = json.loads(raw[inicio:fim])
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"JSON inválido: {exc}. Resposta: {raw[:500]!r}")

    if not isinstance(questoes, list):
        raise HTTPException(status_code=502, detail=f"IA não retornou array. Tipo: {type(questoes).__name__}. Resposta: {raw[:200]!r}")

    return questoes
