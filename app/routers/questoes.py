import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.aluno import Aluno
from app.models.questao import Questao
from app.models.topico import Topico
from app.schemas.questao import FONTES_ADMIN, ImportacaoLoteResponse, QuestaoCreate, QuestaoResponse, QuestaoUpdate

router = APIRouter(prefix="/questoes", tags=["questões"])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _validar_hierarquia(body: QuestaoCreate, db: Session) -> None:
    """Valida que subject, topic e subtopic existem e formam hierarquia coerente."""
    subject = db.query(Topico).filter(Topico.id == body.subject_id, Topico.nivel == 0).first()
    if not subject:
        raise HTTPException(status_code=422, detail="subject_id não encontrado ou não é uma matéria (nivel=0)")

    topic = db.query(Topico).filter(Topico.id == body.topic_id, Topico.nivel == 1).first()
    if not topic:
        raise HTTPException(status_code=422, detail="topic_id não encontrado ou não é um tópico (nivel=1)")
    if topic.parent_id != body.subject_id:
        raise HTTPException(status_code=422, detail="topic_id não pertence ao subject_id informado")

    subtopic = db.query(Topico).filter(Topico.id == body.subtopic_id, Topico.nivel == 2).first()
    if not subtopic:
        raise HTTPException(status_code=422, detail="subtopic_id não encontrado ou não é um subtópico (nivel=2)")
    if subtopic.parent_id != body.topic_id:
        raise HTTPException(status_code=422, detail="subtopic_id não pertence ao topic_id informado")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("", response_model=QuestaoResponse, status_code=201)
def criar_questao(
    body: QuestaoCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cadastra uma nova questão no banco. A fonte 'ia' é reservada para criação automática."""
    if body.fonte == "ia":
        raise HTTPException(
            status_code=422,
            detail="A fonte 'ia' é reservada para questões geradas automaticamente. Escolha outra fonte.",
        )

    _validar_hierarquia(body, db)

    questao = Questao(
        id=str(uuid.uuid4()),
        subject_id=body.subject_id,
        topic_id=body.topic_id,
        subtopic_id=body.subtopic_id,
        enunciado=body.enunciado,
        alternativas_json=json.dumps(body.alternativas.model_dump(), ensure_ascii=False),
        resposta_correta=body.resposta_correta,
        fonte=body.fonte,
        banca=body.banca,
        ano=body.ano,
    )
    db.add(questao)
    db.commit()
    db.refresh(questao)
    return questao


@router.post("/lote", response_model=ImportacaoLoteResponse, status_code=201)
def importar_questoes_lote(
    body: List[QuestaoCreate],
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: importa lista de questões em lote para a tabela usada pela engine pedagógica."""
    importadas = 0
    erros: list[str] = []

    for i, item in enumerate(body, start=1):
        if item.fonte == "ia":
            erros.append(f"Questão {i}: fonte 'ia' é reservada para criação automática")
            continue
        try:
            _validar_hierarquia(item, db)
        except HTTPException as exc:
            erros.append(f"Questão {i}: {exc.detail}")
            continue

        questao = Questao(
            id=str(uuid.uuid4()),
            subject_id=item.subject_id,
            topic_id=item.topic_id,
            subtopic_id=item.subtopic_id,
            enunciado=item.enunciado,
            alternativas_json=json.dumps(item.alternativas.model_dump(), ensure_ascii=False),
            resposta_correta=item.resposta_correta,
            fonte=item.fonte,
            banca=item.banca,
            ano=item.ano,
        )
        db.add(questao)
        importadas += 1

    db.commit()
    return ImportacaoLoteResponse(importadas=importadas, erros=erros)


@router.get("", response_model=List[QuestaoResponse])
def listar_questoes(
    subject_id: Optional[str] = Query(None),
    topic_id: Optional[str] = Query(None),
    subtopic_id: Optional[str] = Query(None),
    fonte: Optional[str] = Query(None, description="ia | admin | qconcursos | tec | prova_real | simulado"),
    banca: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    apenas_ativas: bool = Query(True),
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    """Lista questões com filtros opcionais."""
    q = db.query(Questao)

    if apenas_ativas:
        q = q.filter(Questao.ativo == True)
    if subject_id:
        q = q.filter(Questao.subject_id == subject_id)
    if topic_id:
        q = q.filter(Questao.topic_id == topic_id)
    if subtopic_id:
        q = q.filter(Questao.subtopic_id == subtopic_id)
    if fonte:
        q = q.filter(Questao.fonte == fonte)
    if banca:
        q = q.filter(Questao.banca == banca)
    if ano:
        q = q.filter(Questao.ano == ano)

    return q.order_by(Questao.created_at.desc()).all()


@router.get("/subtopico/{subtopic_id}", response_model=List[QuestaoResponse])
def listar_por_subtopico(
    subtopic_id: str,
    fonte: Optional[str] = Query(None, description="Filtrar por fonte: ia | admin | qconcursos | tec | prova_real | simulado"),
    apenas_ativas: bool = Query(True),
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    """Lista questões de um subtópico específico."""
    subtopic = db.query(Topico).filter(Topico.id == subtopic_id, Topico.nivel == 2).first()
    if not subtopic:
        raise HTTPException(status_code=404, detail="Subtópico não encontrado")

    q = db.query(Questao).filter(Questao.subtopic_id == subtopic_id)
    if apenas_ativas:
        q = q.filter(Questao.ativo == True)
    if fonte:
        q = q.filter(Questao.fonte == fonte)

    return q.order_by(Questao.created_at.desc()).all()


@router.patch("/{questao_id}", response_model=QuestaoResponse)
def editar_questao(
    questao_id: str,
    body: QuestaoUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de uma questão existente."""
    questao = db.query(Questao).filter(Questao.id == questao_id).first()
    if not questao:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    data = body.model_dump(exclude_unset=True)

    if "fonte" in data and data["fonte"] == "ia":
        raise HTTPException(
            status_code=422,
            detail="A fonte 'ia' é reservada para questões geradas automaticamente.",
        )

    if "alternativas" in data and data["alternativas"] is not None:
        questao.alternativas_json = json.dumps(data.pop("alternativas"), ensure_ascii=False)
    else:
        data.pop("alternativas", None)

    for field, value in data.items():
        setattr(questao, field, value)

    db.commit()
    db.refresh(questao)
    return questao
