"""
app/routers/admin_importar_tec.py — Importação de questões do TEC Concursos via PDF.
"""
import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.questao_banco import QuestaoBanco
from app.models.question_subtopic import QuestionSubtopic
from app.models.topico import Topico
from app.routers.admin_importar_questoes import _materia_existe
from app.services.tec_parser import parse_pdf_tec, extrair_texto_debug

router = APIRouter(prefix="/admin", tags=["admin — importar TEC Concursos"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class TecQuestaoPreview(BaseModel):
    id_tec: str
    numero: int
    banca: str
    ano: str
    materia: str
    subtopico_tec: str
    subtopico_id: Optional[str] = None
    subtopico_sugerido: str
    tipo: str
    enunciado: str
    alternativas: List[str]
    gabarito: str


class TecParseResponse(BaseModel):
    total: int
    mapeadas: int
    nao_mapeadas: int
    questoes: List[TecQuestaoPreview]


class TecQuestaoImportar(BaseModel):
    id_tec: str
    banca: Optional[str] = None
    ano: Optional[str] = None
    materia: str
    subject: str
    subtopico_id: Optional[str] = None
    tipo: str
    enunciado: str
    alternativas: List[str]
    gabarito: str


class TecImportarRequest(BaseModel):
    questoes: List[TecQuestaoImportar]


class TecImportarResponse(BaseModel):
    importadas: int
    erros: List[str]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _gerar_code(disciplina: str, banca: str, ano: Optional[str], db: Session) -> str:
    banca_p = (banca or "SEM-BANCA").upper().replace(" ", "-")
    ano_p = ano or "SEM-ANO"
    prefix = f"{disciplina.upper().replace(' ', '_')}-{banca_p}-{ano_p}"
    esc = prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    count = db.query(QuestaoBanco).filter(
        QuestaoBanco.question_code.like(f"{esc}-%", escape="\\")
    ).count()
    return f"{prefix}-{str(count + 1).zfill(4)}"


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/importar-tec-debug")
async def debug_tec_pdf(
    file: UploadFile = File(...),
    _: Aluno = Depends(require_admin),
):
    """Retorna texto bruto extraído pelo pdfplumber (debug)."""
    pdf_bytes = await file.read()
    texto = extrair_texto_debug(pdf_bytes)
    # Mostrar primeiros 3000 chars e primeiras 50 linhas
    linhas = texto.split("\n")
    return {
        "total_chars": len(texto),
        "total_linhas": len(linhas),
        "primeiras_50_linhas": linhas[:50],
        "texto_bruto_3000": texto[:3000],
    }


@router.post("/importar-tec", response_model=TecParseResponse)
async def parsear_tec_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Parseia PDF do TEC Concursos e retorna preview sem salvar."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Envie um arquivo .pdf")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=422, detail="Arquivo PDF vazio")

    try:
        questoes = parse_pdf_tec(pdf_bytes)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Erro ao parsear PDF: {exc}")

    if not questoes:
        raise HTTPException(
            status_code=422,
            detail="Nenhuma questão encontrada. Verifique se é um PDF do TEC Concursos.",
        )

    # Mapear subtópicos por nome (case-insensitive)
    subtopicos = db.query(Topico).filter(Topico.nivel == 2, Topico.ativo == True).all()
    sub_map = {t.nome.lower().strip(): str(t.id) for t in subtopicos}

    mapeadas = 0
    for q in questoes:
        sub_id = sub_map.get(q["subtopico_tec"].lower().strip())
        q["subtopico_id"] = sub_id
        if sub_id:
            mapeadas += 1

    return TecParseResponse(
        total=len(questoes),
        mapeadas=mapeadas,
        nao_mapeadas=len(questoes) - mapeadas,
        questoes=questoes,
    )


@router.post("/importar-tec-confirmar", response_model=TecImportarResponse, status_code=201)
def importar_tec_confirmar(
    body: TecImportarRequest,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Salva as questões TEC revisadas no banco, associando subtópicos quando fornecidos."""
    importadas = 0
    erros: list[str] = []

    for i, item in enumerate(body.questoes, start=1):
        try:
            if item.tipo == "multipla_escolha" and item.alternativas:
                alts = {
                    letra: item.alternativas[idx]
                    for idx, letra in enumerate(["A", "B", "C", "D", "E"])
                    if idx < len(item.alternativas)
                }
                alts_json = json.dumps(alts, ensure_ascii=False)
            else:
                alts_json = json.dumps({}, ensure_ascii=False)

            if not item.gabarito:
                erros.append(f"Questão {i} (TEC {item.id_tec}): gabarito não encontrado — edite antes de importar")
                continue

            code = _gerar_code(item.materia, item.banca or "", item.ano, db)
            questao = QuestaoBanco(
                id=str(uuid.uuid4()),
                question_code=code,
                subject=item.subject or item.materia or "Sem assunto",
                statement=item.enunciado,
                alternatives_json=alts_json,
                correct_answer=item.gabarito,
                board=item.banca or None,
                year=int(item.ano) if item.ano and item.ano.isdigit() else None,
            )
            db.add(questao)
            db.flush()

            if not _materia_existe(item.materia, db):
                questao.materia_pendente = True

            if item.subtopico_id:
                db.add(QuestionSubtopic(
                    id=str(uuid.uuid4()),
                    question_id=str(questao.id),
                    subtopic_id=item.subtopico_id,
                    fonte="manual",
                ))

            db.commit()
            importadas += 1
        except Exception as exc:
            db.rollback()
            erros.append(f"Questão {i} (TEC {item.id_tec}): {exc}")

    return TecImportarResponse(importadas=importadas, erros=erros)
