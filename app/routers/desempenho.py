"""
routers/desempenho.py
GET /desempenho — métricas reais do aluno logado, agregadas por matéria.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.proficiencia import Proficiencia

router = APIRouter(tags=["desempenho"])


# ── Schemas de resposta ────────────────────────────────────────────────────────

class MateriaDesempenho(BaseModel):
    materia: str
    realizadas: int
    acertos: int
    perc: float
    tend_perc_atual: Optional[float] = None
    tend_perc_anterior: Optional[float] = None


class DesempenhoResponse(BaseModel):
    total_questoes: int
    total_acertos: int
    perc_geral: float
    por_materia: list[MateriaDesempenho]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _agrupar_por_materia(registros: list[Proficiencia]) -> dict:
    """Agrega acertos/total por matéria."""
    agrup: dict[str, dict] = {}
    for r in registros:
        mat = r.materia or "Sem matéria"
        if mat not in agrup:
            agrup[mat] = {"acertos": 0, "total": 0}
        agrup[mat]["acertos"] += r.acertos or 0
        agrup[mat]["total"] += r.total or 0
    return agrup


def _perc(acertos: int, total: int) -> float:
    return round(acertos / total * 100, 1) if total > 0 else 0.0


def _tendencia_por_materia(todos: list[Proficiencia]) -> dict[str, tuple[float | None, float | None]]:
    """
    Para cada matéria, retorna (perc_mes_atual, perc_mes_anterior)
    usando os dois meses mais recentes disponíveis nos dados completos.
    """
    from collections import defaultdict

    # materia -> mes (YYYY-MM) -> {acertos, total}
    agrup: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"acertos": 0, "total": 0}))

    for r in todos:
        if not r.data:
            continue
        mes_key = r.data.strftime("%Y-%m")
        mat = r.materia or "Sem matéria"
        agrup[mat][mes_key]["acertos"] += r.acertos or 0
        agrup[mat][mes_key]["total"] += r.total or 0

    resultado: dict[str, tuple[float | None, float | None]] = {}
    for mat, meses in agrup.items():
        meses_ord = sorted(meses.keys())
        if len(meses_ord) >= 2:
            ult = meses[meses_ord[-1]]
            pen = meses[meses_ord[-2]]
            resultado[mat] = (_perc(ult["acertos"], ult["total"]), _perc(pen["acertos"], pen["total"]))
        elif len(meses_ord) == 1:
            ult = meses[meses_ord[-1]]
            resultado[mat] = (_perc(ult["acertos"], ult["total"]), None)
        else:
            resultado[mat] = (None, None)

    return resultado


# ── Endpoint ───────────────────────────────────────────────────────────────────

@router.get("/desempenho", response_model=DesempenhoResponse)
def get_desempenho(
    mes: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mês (1-12)"),
    ano: Optional[int] = Query(None, ge=2000, le=2100, description="Filtrar por ano"),
    fonte: Optional[list[str]] = Query(None, description="Filtrar por fonte(s)"),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Retorna métricas de desempenho do aluno logado, agregadas por matéria.
    Aplica filtros opcionais de mês, ano e fonte.
    A tendência é calculada sempre sobre o histórico completo.
    """
    # Todos os registros (para calcular tendência)
    q_todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id)
    todos = q_todos.all()

    # Registros filtrados
    q_filtrado = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id)

    if mes:
        from sqlalchemy import extract
        q_filtrado = q_filtrado.filter(extract("month", Proficiencia.data) == mes)
    if ano:
        from sqlalchemy import extract
        q_filtrado = q_filtrado.filter(extract("year", Proficiencia.data) == ano)
    if fonte:
        q_filtrado = q_filtrado.filter(Proficiencia.fonte.in_(fonte))

    filtrados = q_filtrado.all()

    # Tendência (histórico completo)
    tendencias = _tendencia_por_materia(todos)

    # Agregação por matéria (dados filtrados)
    agrup = _agrupar_por_materia(filtrados)

    total_q = sum(v["total"] for v in agrup.values())
    total_a = sum(v["acertos"] for v in agrup.values())

    por_materia = []
    for mat, vals in sorted(agrup.items(), key=lambda x: -_perc(x[1]["acertos"], x[1]["total"])):
        tend_atual, tend_ant = tendencias.get(mat, (None, None))
        por_materia.append(MateriaDesempenho(
            materia=mat,
            realizadas=vals["total"],
            acertos=vals["acertos"],
            perc=_perc(vals["acertos"], vals["total"]),
            tend_perc_atual=tend_atual,
            tend_perc_anterior=tend_ant,
        ))

    return DesempenhoResponse(
        total_questoes=total_q,
        total_acertos=total_a,
        perc_geral=_perc(total_a, total_q),
        por_materia=por_materia,
    )
