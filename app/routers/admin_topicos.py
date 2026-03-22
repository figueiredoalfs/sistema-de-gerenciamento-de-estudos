import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.question_subtopic import QuestionSubtopic
from app.models.subtopico_area import SubtopicoArea
from app.models.topico import Topico
from app.schemas.topico import (
    MateriaHierarquia,
    BlocoHierarquia,
    SubtopicoHierarquia,
    SubtopicoAreaResponse,
    SubtopicoAreaUpsert,
    TopicoCreate,
    TopicoResponse,
    TopicoUpdate,
)

router = APIRouter(prefix="/admin/topicos", tags=["admin - tópicos"])


# ─── Hierarquia ───────────────────────────────────────────────────────────────

@router.get("/hierarquia", response_model=List[MateriaHierarquia])
def hierarquia_topicos(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: retorna árvore completa matéria→bloco→subtópico com contadores."""
    # Contagens de questões por subtópico
    contagens: Dict[str, int] = {
        row[0]: row[1]
        for row in (
            db.query(QuestionSubtopic.subtopic_id, func.count(QuestionSubtopic.question_id))
            .group_by(QuestionSubtopic.subtopic_id)
            .all()
        )
    }

    # SubtopicoArea configs indexadas por subtopico_id
    todas_areas = db.query(SubtopicoArea).all()
    areas_por_sub: Dict[str, List[SubtopicoArea]] = {}
    for sa_row in todas_areas:
        areas_por_sub.setdefault(sa_row.subtopico_id, []).append(sa_row)

    materias = (
        db.query(Topico)
        .filter(Topico.nivel == 0)
        .order_by(Topico.nome)
        .all()
    )

    resultado = []
    for mat in materias:
        blocos_db = (
            db.query(Topico)
            .filter(Topico.nivel == 1, Topico.parent_id == mat.id)
            .order_by(Topico.nome)
            .all()
        )
        blocos_out = []
        for bloco in blocos_db:
            subs_db = (
                db.query(Topico)
                .filter(Topico.nivel == 2, Topico.parent_id == bloco.id)
                .order_by(Topico.nome)
                .all()
            )
            subs_out = [
                SubtopicoHierarquia(
                    id=s.id,
                    nome=s.nome,
                    nivel=s.nivel,
                    ativo=s.ativo,
                    peso_edital=s.peso_edital,
                    prerequisitos_json=s.prerequisitos_json or "[]",
                    num_questoes=contagens.get(s.id, 0),
                    areas=[
                        SubtopicoAreaResponse(
                            id=a.id,
                            subtopico_id=a.subtopico_id,
                            area=a.area,
                            peso=a.peso,
                            complexidade=a.complexidade,
                        )
                        for a in areas_por_sub.get(s.id, [])
                    ],
                )
                for s in subs_db
            ]
            blocos_out.append(
                BlocoHierarquia(
                    id=bloco.id,
                    nome=bloco.nome,
                    nivel=bloco.nivel,
                    ativo=bloco.ativo,
                    subtopicos=subs_out,
                )
            )
        resultado.append(
            MateriaHierarquia(
                id=mat.id,
                nome=mat.nome,
                nivel=mat.nivel,
                ativo=mat.ativo,
                blocos=blocos_out,
            )
        )
    return resultado


# ─── CRUD básico ──────────────────────────────────────────────────────────────

@router.post("", response_model=TopicoResponse, status_code=201)
def criar_topico(
    body: TopicoCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cria matéria (nivel=0), bloco (nivel=1) ou tópico (nivel=2)."""
    if body.parent_id:
        parent = db.query(Topico).filter(Topico.id == body.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Tópico pai não encontrado")

    topico = Topico(
        id=str(uuid.uuid4()),
        nome=body.nome,
        nivel=body.nivel,
        parent_id=body.parent_id,
        descricao=body.descricao,
        area=body.area,
        banca=body.banca,
        peso_edital=body.peso_edital,
        decay_rate=body.decay_rate,
        dependencias_json=body.dependencias_json,
        prerequisitos_json=body.prerequisitos_json,
    )
    db.add(topico)
    db.commit()
    db.refresh(topico)
    return topico


@router.get("", response_model=List[TopicoResponse])
def listar_topicos(
    nivel: Optional[int] = Query(None, description="Filtrar por nível: 0=matéria, 1=bloco, 2=tópico"),
    area: Optional[str] = Query(None),
    banca: Optional[str] = Query(None),
    parent_id: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista tópicos com filtros opcionais."""
    q = db.query(Topico)
    if apenas_ativos:
        q = q.filter(Topico.ativo == True)
    if nivel is not None:
        q = q.filter(Topico.nivel == nivel)
    if area:
        q = q.filter(Topico.area == area)
    if banca:
        q = q.filter(Topico.banca == banca)
    if parent_id:
        q = q.filter(Topico.parent_id == parent_id)
    return q.order_by(Topico.nivel, Topico.nome).all()


@router.get("/questoes-por-subtopico", response_model=Dict[str, int])
def questoes_por_subtopico(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: retorna contagem de questões por subtópico {subtopic_id: count}."""
    rows = (
        db.query(QuestionSubtopic.subtopic_id, func.count(QuestionSubtopic.question_id))
        .group_by(QuestionSubtopic.subtopic_id)
        .all()
    )
    return {row[0]: row[1] for row in rows}


@router.get("/{topico_id}", response_model=TopicoResponse)
def detalhe_topico(
    topico_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: retorna detalhes de um tópico."""
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")
    return topico


@router.patch("/{topico_id}", response_model=TopicoResponse)
def editar_topico(
    topico_id: str,
    body: TopicoUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: edita campos de um tópico."""
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(topico, field, value)

    db.commit()
    db.refresh(topico)
    return topico


@router.delete("/{topico_id}", status_code=204)
def desativar_topico(
    topico_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: desativa um tópico (soft-delete).
    Bloqueado se subtópico (nivel=2) tiver questões vinculadas.
    """
    topico = db.query(Topico).filter(Topico.id == topico_id).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")

    if topico.nivel == 2:
        count = (
            db.query(func.count(QuestionSubtopic.id))
            .filter(QuestionSubtopic.subtopic_id == topico_id)
            .scalar()
        )
        if count and count > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Subtópico possui {count} questão(ões) vinculada(s). Remova-as antes de desativar.",
            )

    topico.ativo = False
    db.commit()


# ─── SubtopicoArea ────────────────────────────────────────────────────────────

@router.get("/{subtopico_id}/areas", response_model=List[SubtopicoAreaResponse])
def listar_areas_subtopico(
    subtopico_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: lista configurações de área para um subtópico."""
    topico = db.query(Topico).filter(Topico.id == subtopico_id, Topico.nivel == 2).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Subtópico não encontrado")
    return db.query(SubtopicoArea).filter(SubtopicoArea.subtopico_id == subtopico_id).all()


@router.patch("/{subtopico_id}/area", response_model=SubtopicoAreaResponse)
def configurar_area_subtopico(
    subtopico_id: str,
    body: SubtopicoAreaUpsert,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Admin: cria ou atualiza configuração de peso/complexidade de um subtópico por área."""
    topico = db.query(Topico).filter(Topico.id == subtopico_id, Topico.nivel == 2).first()
    if not topico:
        raise HTTPException(status_code=404, detail="Subtópico não encontrado")

    config = (
        db.query(SubtopicoArea)
        .filter(
            SubtopicoArea.subtopico_id == subtopico_id,
            SubtopicoArea.area == body.area,
        )
        .first()
    )
    if config:
        config.peso = body.peso
        config.complexidade = body.complexidade
    else:
        config = SubtopicoArea(
            id=str(uuid.uuid4()),
            subtopico_id=subtopico_id,
            area=body.area,
            peso=body.peso,
            complexidade=body.complexidade,
        )
        db.add(config)

    db.commit()
    db.refresh(config)
    return config
