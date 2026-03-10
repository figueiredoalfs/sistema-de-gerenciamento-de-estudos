"""
services/priorizacao.py
Algoritmo de priorização de sessões — ConcursoAI

Fórmula (docs/ALGORITMO.md):
  Score = W1*Urgencia + W2*Lacuna + W3*Peso + W4*FatorErros

  Urgencia   = 1 - (dias_restantes / dias_totais)^0.5
  Lacuna     = 1 - (taxa_acerto/100) * exp(-lambda * dias_desde_estudo)
  Peso       = peso_edital_topico / max(pesos no cronograma)
  FatorErros = min(erros_pendentes / 10.0, 1.0)

Pesos default: W1=0.35 W2=0.30 W3=0.20 W4=0.15 (ajustaveis via ConfigSistema)
Interleaving: max 2 sessoes da mesma materia/area no resultado final.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.config_sistema import ConfigSistema
from app.models.erro_critico import ErroCritico
from app.models.proficiencia import Proficiencia
from app.models.sessao import Sessao
from app.models.topico import Topico

# Pesos default
W_DEFAULT = {"w1": 0.35, "w2": 0.30, "w3": 0.20, "w4": 0.15}


@dataclass
class ScoreBreakdown:
    urgencia: float
    lacuna: float
    peso: float
    fator_erros: float
    score: float


@dataclass
class SessaoPriorizada:
    sessao_id: str
    topico_id: Optional[str]
    topico_nome: str
    area: str
    tipo: str
    duracao_planejada_min: int
    confianca: str
    score: float
    breakdown: ScoreBreakdown


def _get_pesos(db: Session) -> dict:
    """Lê W1-W4 do ConfigSistema; usa defaults se não configurado."""
    pesos = dict(W_DEFAULT)
    registros = (
        db.query(ConfigSistema)
        .filter(ConfigSistema.chave.in_(["w1", "w2", "w3", "w4"]))
        .all()
    )
    for r in registros:
        try:
            pesos[r.chave] = float(r.valor)
        except (ValueError, TypeError):
            pass
    return pesos


def _proficiencia_composta(profs: list[Proficiencia]) -> tuple[float, Optional[datetime]]:
    """
    Calcula taxa de acerto composta ponderada por peso_fonte.
    Retorna (percentual_ponderado, data_mais_recente).
    """
    if not profs:
        return 0.0, None

    soma_pesos = sum(p.peso_fonte for p in profs)
    if soma_pesos == 0:
        return 0.0, None

    percentual = sum(p.percentual * p.peso_fonte for p in profs) / soma_pesos
    data_max = max((p.data for p in profs if p.data), default=None)
    return percentual, data_max


def _calcular_urgencia(aluno: Aluno, sessao_created_at: datetime) -> float:
    """Urgencia = 1 - (dias_restantes / dias_totais)^0.5"""
    agora = datetime.now(timezone.utc)

    if not aluno.data_prova:
        return 0.5  # sem data de prova: urgência média

    data_prova = aluno.data_prova
    if data_prova.tzinfo is None:
        data_prova = data_prova.replace(tzinfo=timezone.utc)

    dias_restantes = max((data_prova - agora).days, 0)

    inicio = sessao_created_at
    if inicio.tzinfo is None:
        inicio = inicio.replace(tzinfo=timezone.utc)
    dias_totais = max((data_prova - inicio).days, 1)

    ratio = min(dias_restantes / dias_totais, 1.0)
    return round(1.0 - math.sqrt(ratio), 4)


def _calcular_lacuna(percentual: float, decay_rate: float, data_estudo: Optional[datetime]) -> float:
    """Lacuna = 1 - (taxa_acerto/100) * exp(-lambda * dias_desde_estudo)"""
    agora = datetime.now(timezone.utc)

    if data_estudo:
        if data_estudo.tzinfo is None:
            data_estudo = data_estudo.replace(tzinfo=timezone.utc)
        dias = max((agora - data_estudo).days, 0)
    else:
        dias = 0

    taxa = percentual / 100.0
    lacuna = 1.0 - taxa * math.exp(-decay_rate * dias)
    return round(max(0.0, min(1.0, lacuna)), 4)


def _calcular_fator_erros(topico_id: Optional[str], materia: Optional[str], aluno_id: str, db: Session) -> float:
    """FatorErros = min(erros_pendentes / 10.0, 1.0)"""
    query = db.query(ErroCritico).filter(
        ErroCritico.aluno_id == aluno_id,
        ErroCritico.status == "pendente",
    )
    if topico_id:
        query = query.filter(ErroCritico.topico_id == topico_id)
    elif materia:
        query = query.filter(ErroCritico.materia == materia)

    erros = query.count()
    return round(min(erros / 10.0, 1.0), 4)


def calcular_agenda(
    aluno_id: str,
    db: Session,
    top: int = 5,
) -> list[SessaoPriorizada]:
    """
    Calcula e retorna as top-N sessões priorizadas para o aluno.
    Aplica interleaving: max 2 sessões da mesma área no resultado.
    """
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        return []

    pesos = _get_pesos(db)
    w1, w2, w3, w4 = pesos["w1"], pesos["w2"], pesos["w3"], pesos["w4"]

    # Sessões pendentes do aluno
    sessoes = (
        db.query(Sessao)
        .filter(Sessao.aluno_id == aluno_id, Sessao.concluida == False)
        .all()
    )

    if not sessoes:
        return []

    # Max peso_edital para normalização
    topico_ids = [s.topico_id for s in sessoes if s.topico_id]
    if topico_ids:
        topicos_map = {
            t.id: t
            for t in db.query(Topico).filter(Topico.id.in_(topico_ids)).all()
        }
        max_peso = max((t.peso_edital for t in topicos_map.values()), default=1.0) or 1.0
    else:
        topicos_map = {}
        max_peso = 1.0

    # Proficiências do aluno agrupadas por topico_id
    profs_por_topico: dict[str, list[Proficiencia]] = {}
    profs_por_materia: dict[str, list[Proficiencia]] = {}
    all_profs = db.query(Proficiencia).filter(Proficiencia.aluno_id == aluno_id).all()
    for p in all_profs:
        if p.topico_id:
            profs_por_topico.setdefault(p.topico_id, []).append(p)
        if p.materia:
            profs_por_materia.setdefault(p.materia, []).append(p)

    resultados: list[tuple[float, SessaoPriorizada]] = []

    for sessao in sessoes:
        topico = topicos_map.get(sessao.topico_id) if sessao.topico_id else None
        topico_nome = topico.nome if topico else "Tópico geral"
        area = topico.area if topico else ""
        decay = topico.decay_rate if topico else 0.05
        peso_edital = topico.peso_edital if topico else 1.0

        # Proficiência relevante
        profs = (
            profs_por_topico.get(sessao.topico_id, [])
            if sessao.topico_id
            else profs_por_materia.get(area, [])
        )
        percentual, data_estudo = _proficiencia_composta(profs)

        # Componentes do score
        urgencia = _calcular_urgencia(aluno, sessao.created_at)
        lacuna = _calcular_lacuna(percentual, decay, data_estudo)
        peso_norm = round(peso_edital / max_peso, 4)
        fator_erros = _calcular_fator_erros(sessao.topico_id, area, aluno_id, db)

        score = round(w1 * urgencia + w2 * lacuna + w3 * peso_norm + w4 * fator_erros, 4)

        sp = SessaoPriorizada(
            sessao_id=sessao.id,
            topico_id=sessao.topico_id,
            topico_nome=topico_nome,
            area=area,
            tipo=sessao.tipo,
            duracao_planejada_min=sessao.duracao_planejada_min or 0,
            confianca=sessao.confianca,
            score=score,
            breakdown=ScoreBreakdown(
                urgencia=urgencia,
                lacuna=lacuna,
                peso=peso_norm,
                fator_erros=fator_erros,
                score=score,
            ),
        )
        resultados.append((score, sp))

    # Ordena por score desc
    resultados.sort(key=lambda x: x[0], reverse=True)

    # Interleaving: max 2 sessoes da mesma area
    contagem_area: dict[str, int] = {}
    agenda: list[SessaoPriorizada] = []
    for _, sp in resultados:
        area_key = sp.area or "sem_area"
        if contagem_area.get(area_key, 0) >= 2:
            continue
        contagem_area[area_key] = contagem_area.get(area_key, 0) + 1
        agenda.append(sp)
        if len(agenda) >= top:
            break

    return agenda
