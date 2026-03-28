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


class EvolucaoPonto(BaseModel):
    materia: str
    mes: str  # "YYYY-MM"
    acertos: int
    total: int
    perc: float


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


@router.get("/desempenho/resumo")
def get_resumo(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    KPIs globais: taxa de acerto, total de questões, streak, dias estudados.
    """
    from datetime import date, timedelta
    from collections import defaultdict

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()

    total_q = sum(p.total for p in todos)
    total_a = sum(p.acertos for p in todos)
    perc_geral = _perc(total_a, total_q)

    # Dias únicos com atividade (usando data da proficiencia)
    datas_unicas = set()
    for p in todos:
        if p.data:
            datas_unicas.add(p.data.date() if hasattr(p.data, 'date') else p.data)

    hoje = date.today()
    trinta_dias = hoje - timedelta(days=30)
    dias_30d = len([d for d in datas_unicas if d >= trinta_dias])

    # Streak: dias consecutivos até hoje (ou ontem)
    streak = 0
    dia_atual = hoje
    while dia_atual in datas_unicas:
        streak += 1
        dia_atual -= timedelta(days=1)
    if streak == 0:
        ontem = hoje - timedelta(days=1)
        dia_atual = ontem
        while dia_atual in datas_unicas:
            streak += 1
            dia_atual -= timedelta(days=1)

    # Por matéria
    agrup = _agrupar_por_materia(todos)
    materias = [
        {
            "nome": mat,
            "taxa_acerto": _perc(v["acertos"], v["total"]),
            "total_questoes": v["total"],
            "status": "dominado" if _perc(v["acertos"], v["total"]) >= 70
                      else "atenção" if _perc(v["acertos"], v["total"]) >= 50
                      else "crítico",
        }
        for mat, v in sorted(agrup.items(), key=lambda x: -_perc(x[1]["acertos"], x[1]["total"]))
    ]

    return {
        "taxa_acerto_geral": perc_geral,
        "total_questoes": total_q,
        "streak_dias": streak,
        "dias_estudados_30d": dias_30d,
        "materias": materias,
    }


@router.get("/desempenho/subtopicos-criticos")
def get_subtopicos_criticos(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Lista os subtópicos com pior desempenho do aluno.
    """
    from datetime import date, timedelta
    from collections import defaultdict

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()

    # Agrupar por (topico_id ou subtopico) para calcular taxa agregada
    agrup: dict = defaultdict(lambda: {"acertos": 0, "total": 0, "materia": "", "subtopico": "", "topico_id": None, "ultima_data": None})
    for p in todos:
        chave = p.topico_id or p.subtopico or "?"
        agrup[chave]["acertos"] += p.acertos or 0
        agrup[chave]["total"] += p.total or 0
        agrup[chave]["materia"] = p.materia or ""
        agrup[chave]["subtopico"] = p.subtopico or ""
        agrup[chave]["topico_id"] = p.topico_id
        if p.data:
            d = p.data.date() if hasattr(p.data, 'date') else p.data
            if agrup[chave]["ultima_data"] is None or d > agrup[chave]["ultima_data"]:
                agrup[chave]["ultima_data"] = d

    hoje = date.today()
    resultado = []
    for chave, v in agrup.items():
        if v["total"] == 0:
            continue
        taxa = _perc(v["acertos"], v["total"])
        dias_sem = (hoje - v["ultima_data"]).days if v["ultima_data"] else 999
        resultado.append({
            "topico_id": v["topico_id"],
            "materia": v["materia"],
            "subtopico": v["subtopico"],
            "taxa_acerto": taxa,
            "total_questoes": v["total"],
            "dias_sem_revisar": dias_sem,
        })

    resultado.sort(key=lambda x: (x["taxa_acerto"], -x["dias_sem_revisar"]))
    return resultado[:limit]


@router.get("/desempenho/sugestoes-revisao")
def get_sugestoes_revisao(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Subtópicos que precisam de revisão, ordenados por prioridade.
    Algoritmo:
      - taxa < 50%: crítico
      - taxa < 70% + sem revisão > 7 dias: urgente
      - sem revisão > 14 dias: revisar
    """
    todos = get_subtopicos_criticos(limit=50, db=db, usuario=usuario)
    sugestoes = []
    for item in todos:
        taxa = item["taxa_acerto"]
        dias = item["dias_sem_revisar"]
        if taxa < 50:
            prioridade = "critico"
        elif taxa < 70 and dias > 7:
            prioridade = "urgente"
        elif dias > 14:
            prioridade = "revisar"
        else:
            continue
        sugestoes.append({**item, "prioridade": prioridade})
    return sugestoes


@router.get("/desempenho/evolucao", response_model=list[EvolucaoPonto])
def get_evolucao(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Retorna a evolução mensal de desempenho por matéria.
    Cada ponto representa o % de acertos em um mês para uma matéria.
    """
    from collections import defaultdict

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()

    agrup: dict[tuple, dict] = defaultdict(lambda: {"acertos": 0, "total": 0})
    for r in todos:
        if not r.data or not r.materia:
            continue
        chave = (r.materia, r.data.strftime("%Y-%m"))
        agrup[chave]["acertos"] += r.acertos or 0
        agrup[chave]["total"] += r.total or 0

    return [
        EvolucaoPonto(
            materia=mat,
            mes=mes,
            acertos=v["acertos"],
            total=v["total"],
            perc=_perc(v["acertos"], v["total"]),
        )
        for (mat, mes), v in sorted(agrup.items(), key=lambda x: (x[0][1], x[0][0]))
    ]


# ── Endpoints V1-T07 ───────────────────────────────────────────────────────────

def _filtrar_por_periodo(registros, periodo: str):
    """Filtra lista de Proficiencia pelo período: '7d', '30d', '90d' ou 'tudo'."""
    from datetime import date, timedelta
    if periodo == "tudo" or not periodo:
        return registros
    dias = {"7d": 7, "30d": 30, "90d": 90}.get(periodo, None)
    if dias is None:
        return registros
    corte = date.today() - timedelta(days=dias)
    return [p for p in registros if p.data and (p.data.date() if hasattr(p.data, 'date') else p.data) >= corte]


@router.get("/desempenho/por-materia")
def get_por_materia(
    periodo: str = Query("tudo", description="7d | 30d | 90d | tudo"),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    from collections import defaultdict

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()
    filtrados = _filtrar_por_periodo(todos, periodo)

    # Por matéria com evolução semanal
    by_mat: dict = defaultdict(lambda: {"acertos": 0, "total": 0, "semanas": defaultdict(lambda: {"acertos": 0, "total": 0})})
    for p in filtrados:
        mat = p.materia or "Sem matéria"
        by_mat[mat]["acertos"] += p.acertos or 0
        by_mat[mat]["total"] += p.total or 0
        if p.data:
            d = p.data.date() if hasattr(p.data, 'date') else p.data
            from datetime import timedelta
            # Início da semana (segunda-feira)
            inicio_semana = d - timedelta(days=d.weekday())
            semana_key = inicio_semana.isoformat()
            by_mat[mat]["semanas"][semana_key]["acertos"] += p.acertos or 0
            by_mat[mat]["semanas"][semana_key]["total"] += p.total or 0

    resultado = []
    for mat, v in sorted(by_mat.items(), key=lambda x: -_perc(x[1]["acertos"], x[1]["total"])):
        evolucao_semanal = [
            {"semana": sem, "taxa": _perc(sv["acertos"], sv["total"])}
            for sem, sv in sorted(v["semanas"].items())
        ]
        resultado.append({
            "materia": mat,
            "taxa_acerto": _perc(v["acertos"], v["total"]),
            "total_questoes": v["total"],
            "evolucao_semanal": evolucao_semanal,
        })
    return resultado


@router.get("/desempenho/heatmap-subtopicos")
def get_heatmap_subtopicos(
    periodo: str = Query("tudo", description="7d | 30d | 90d | tudo"),
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    from collections import defaultdict

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()
    filtrados = _filtrar_por_periodo(todos, periodo)

    agrup: dict = defaultdict(lambda: {"acertos": 0, "total": 0, "materia": "", "subtopico": ""})
    for p in filtrados:
        chave = p.topico_id or p.subtopico or "?"
        agrup[chave]["acertos"] += p.acertos or 0
        agrup[chave]["total"] += p.total or 0
        agrup[chave]["materia"] = p.materia or ""
        agrup[chave]["subtopico"] = p.subtopico or ""

    resultado = []
    for chave, v in agrup.items():
        if v["total"] == 0:
            continue
        taxa = _perc(v["acertos"], v["total"])
        status = "dominado" if taxa >= 70 else "atenção" if taxa >= 50 else "crítico"
        resultado.append({
            "topico_id": chave,
            "materia": v["materia"],
            "subtopico": v["subtopico"],
            "taxa_acerto": taxa,
            "total_questoes": v["total"],
            "status": status,
        })

    resultado.sort(key=lambda x: (x["materia"], x["subtopico"]))
    return resultado


@router.get("/desempenho/volume-semanal")
def get_volume_semanal(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Últimas 8 semanas — volume de questões por matéria."""
    from datetime import date, timedelta
    from collections import defaultdict

    hoje = date.today()
    oito_semanas = hoje - timedelta(weeks=8)

    todos = db.query(Proficiencia).filter(
        Proficiencia.aluno_id == usuario.id,
    ).all()

    # Agrupar por semana e matéria
    semanas: dict = defaultdict(lambda: defaultdict(int))
    for p in todos:
        if not p.data:
            continue
        d = p.data.date() if hasattr(p.data, 'date') else p.data
        if d < oito_semanas:
            continue
        inicio = d - timedelta(days=d.weekday())
        semanas[inicio.isoformat()][p.materia or "Outros"] += p.total or 0

    semanas_ord = sorted(semanas.keys())
    materias = set()
    for sv in semanas.values():
        materias.update(sv.keys())

    return [
        {
            "semana": sem,
            "total_questoes": sum(semanas[sem].values()),
            "por_materia": dict(semanas[sem]),
        }
        for sem in semanas_ord
    ]


@router.get("/desempenho/consistencia")
def get_consistencia(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Últimos 365 dias — atividade diária."""
    from datetime import date, timedelta
    from collections import defaultdict

    corte = date.today() - timedelta(days=365)
    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()

    dias: dict = defaultdict(lambda: {"total_questoes": 0, "total_minutos": 0})
    for p in todos:
        if not p.data:
            continue
        d = p.data.date() if hasattr(p.data, 'date') else p.data
        if d < corte:
            continue
        dias[d.isoformat()]["total_questoes"] += p.total or 0

    return [{"data": d, **v} for d, v in sorted(dias.items())]


@router.get("/desempenho/por-banca")
def get_por_banca(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Taxa de acerto por banca examinadora."""
    from collections import defaultdict

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()
    agrup: dict = defaultdict(lambda: {"acertos": 0, "total": 0})
    for p in todos:
        banca = p.banca or "Sem banca"
        agrup[banca]["acertos"] += p.acertos or 0
        agrup[banca]["total"] += p.total or 0

    return [
        {"banca": b, "taxa_acerto": _perc(v["acertos"], v["total"]), "total_questoes": v["total"]}
        for b, v in sorted(agrup.items(), key=lambda x: -_perc(x[1]["acertos"], x[1]["total"]))
        if v["total"] > 0
    ]


@router.get("/desempenho/por-banco-questoes")
def get_por_banco_questoes(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """Taxa de acerto por banco de questões (fonte)."""
    from collections import defaultdict

    FONTE_LABEL = {
        "tec": "TEC Concursos",
        "qconcursos": "Qconcursos",
        "simulado": "Simulado Próprio",
        "prova_anterior_mesma_banca": "Prova Anterior (mesma banca)",
        "prova_anterior_outra_banca": "Prova Anterior (outra banca)",
        "manual": "Outro",
        "quiz_ia": "Quiz IA",
        "curso": "Curso",
        "calibracao": "Calibração",
    }

    todos = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario.id).all()
    agrup: dict = defaultdict(lambda: {"acertos": 0, "total": 0})
    for p in todos:
        label = FONTE_LABEL.get(p.fonte or "manual", p.fonte or "manual")
        agrup[label]["acertos"] += p.acertos or 0
        agrup[label]["total"] += p.total or 0

    return [
        {"banco": b, "taxa_acerto": _perc(v["acertos"], v["total"]), "total_questoes": v["total"]}
        for b, v in sorted(agrup.items(), key=lambda x: -_perc(x[1]["acertos"], x[1]["total"]))
        if v["total"] > 0
    ]
