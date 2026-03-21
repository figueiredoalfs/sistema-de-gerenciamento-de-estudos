"""
Endpoints de bateria de questões.

POST /bateria         — registrar bateria multidisciplinar
GET  /baterias        — histórico paginado do aluno
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.proficiencia import PESO_POR_FONTE, Proficiencia
from app.schemas.bateria import BateriaRequest, BateriaResponse, BateriaResumo, ProficienciaOut

router = APIRouter(tags=["bateria"])

# Fontes válidas aceitas pelo endpoint
FONTES_VALIDAS = set(PESO_POR_FONTE.keys())


# ── Hierarquia de tópicos (uso público — para popular selects) ──────────────

@router.get("/topicos/hierarquia", tags=["bateria"])
def get_hierarquia(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Retorna as materias do plano do aluno (filtradas pela area dele)
    com seus subtopicos (nivel=1) para popular os selects de lançamento de bateria.
    """
    from app.models.topico import Topico

    area_key = (usuario.area or "").lower()
    q = db.query(Topico).filter(Topico.nivel == 0, Topico.ativo == True)
    if area_key:
        q = q.filter(Topico.area == area_key)
    materias = q.order_by(Topico.nome).all()

    resultado = []
    for mat in materias:
        subs = (
            db.query(Topico)
            .filter(Topico.parent_id == mat.id, Topico.ativo == True)
            .order_by(Topico.nome)
            .all()
        )
        resultado.append({
            "id": mat.id,
            "nome": mat.nome,
            "subtopicos": [{"id": s.id, "nome": s.nome} for s in subs],
        })

    return resultado


@router.post("/bateria", response_model=BateriaResponse, status_code=201)
def registrar_bateria(
    body: BateriaRequest,
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    """
    Registra uma bateria multidisciplinar.
    Cada questão gera um registro Proficiencia com peso_fonte aplicado.
    confianca='baixa' é o default em toda estimativa nova (F-02).
    """
    bateria_id = str(uuid.uuid4())
    agora = datetime.now(timezone.utc)
    registros: List[Proficiencia] = []

    for q in body.questoes:
        fonte = q.fonte if q.fonte in FONTES_VALIDAS else "qconcursos"
        percentual = (q.acertos / q.total * 100) if q.total > 0 else 0.0
        peso = PESO_POR_FONTE.get(fonte, 1.0)

        prof = Proficiencia(
            id=str(uuid.uuid4()),
            aluno_id=aluno.id,
            topico_id=q.topico_id,
            id_bateria=bateria_id,
            materia=q.materia,
            subtopico=q.subtopico,
            acertos=q.acertos,
            total=q.total,
            percentual=percentual,
            fonte=fonte,
            peso_fonte=peso,
            data=agora,
        )
        db.add(prof)
        registros.append(prof)

    db.commit()
    for r in registros:
        db.refresh(r)

    return BateriaResponse(
        bateria_id=bateria_id,
        total_questoes=sum(q.total for q in body.questoes),
        proficiencias=[ProficienciaOut.model_validate(r) for r in registros],
        mensagem=f"Bateria registrada: {len(registros)} matéria(s), {sum(q.total for q in body.questoes)} questões.",
    )


@router.get("/baterias", response_model=List[BateriaResumo])
def listar_baterias(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    """Histórico de baterias do aluno, paginado, mais recente primeiro."""
    # Busca todas as proficiencias com id_bateria definido
    profs = (
        db.query(Proficiencia)
        .filter(
            Proficiencia.aluno_id == aluno.id,
            Proficiencia.id_bateria.isnot(None),
        )
        .order_by(Proficiencia.data.desc())
        .all()
    )

    # Agrupa por bateria_id
    baterias: dict = {}
    for p in profs:
        bid = p.id_bateria
        if bid not in baterias:
            baterias[bid] = {
                "bateria_id": bid,
                "data": p.data,
                "total_questoes": 0,
                "total_acertos": 0,
                "materias": set(),
            }
        baterias[bid]["total_questoes"] += p.total
        baterias[bid]["total_acertos"] += p.acertos
        baterias[bid]["materias"].add(p.materia or "")

    lista = sorted(baterias.values(), key=lambda x: x["data"], reverse=True)

    # Paginação
    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    pagina_lista = lista[inicio:fim]

    return [
        BateriaResumo(
            bateria_id=b["bateria_id"],
            data=b["data"],
            total_questoes=b["total_questoes"],
            total_acertos=b["total_acertos"],
            percentual_geral=round(b["total_acertos"] / b["total_questoes"] * 100, 1) if b["total_questoes"] else 0.0,
            materias=list(b["materias"]),
        )
        for b in pagina_lista
    ]
