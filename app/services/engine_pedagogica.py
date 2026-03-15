"""
services/engine_pedagogica.py — Engine pedagógica de geração de Metas.

Regras implementadas:
  1. Analisa o progresso do aluno em cada subtópico (RespostaQuestao).
  2. Classifica o estado: novo | em_estudo | em_revisao | dominado.
  3. Usa exposure_count e accuracy_rate por subtópico.
  4. Prioridade: revisões pendentes > reforços > novos subtópicos.
  5. Reforço quando abaixo do limiar progressivo:
       exposure 1 → 60% | exposure 2 → 70% | exposure 3+ → 80% | domínio → 85%
  6. Ciclo por subtópico: teoria → revisao → questionario → reforco (se necessário).
  7. Task teoria inclui questionário curto de validação (5 questões em questoes_json).
  8. Task questionario inclui bateria de 20-30 questões.
  9. Alternância automática de matérias via round-robin.
 10. Peso do subtópico no edital (peso_edital) define ordem de novos conteúdos.
 11. Todas as tasks recebem goal_id vinculado à Meta gerada.
"""

import json
import random
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.meta import Meta
from app.models.questao import Questao
from app.models.resposta_questao import RespostaQuestao
from app.models.study_task import StudyTask
from app.models.subtopico_estado import SubtopicoEstado
from app.models.topico import Topico
from app.services.gerador_cronograma import (
    _subjects_do_ciclo,
    _subjects_fallback,
    _subtopicos_da_materia,
)

# ---------------------------------------------------------------------------
# Constantes de limiares de acerto
# ---------------------------------------------------------------------------
LIMIARES: dict[int, float] = {
    1: 0.60,
    2: 0.70,
    3: 0.80,
}
LIMIAR_DOMINIO: float = 0.85
LIMIAR_DEFAULT: float = 0.80  # exposure_count >= 4


# ---------------------------------------------------------------------------
# Helpers de estado
# ---------------------------------------------------------------------------

def _limiar_para(exposure_count: int) -> float:
    return LIMIARES.get(exposure_count, LIMIAR_DEFAULT)


def _calcular_estado(exposure_count: int, accuracy_rate: float) -> str:
    if exposure_count == 0:
        return "novo"
    if accuracy_rate >= LIMIAR_DOMINIO:
        return "dominado"
    limiar = _limiar_para(exposure_count)
    if accuracy_rate >= limiar:
        return "em_revisao"
    return "em_estudo"


def _precisa_reforco(exposure_count: int, accuracy_rate: float) -> bool:
    if exposure_count == 0:
        return False
    return accuracy_rate < _limiar_para(exposure_count)


def _tipo_task(est: Optional[SubtopicoEstado]) -> str:
    """
    Determina o tipo pedagógico da task com base no estado do subtópico.

    Ciclo por subtópico:
        novo          → teoria
        em_revisao    → revisao
        em_estudo (abaixo limiar) → reforco
        em_estudo (acima limiar)  → questionario
    """
    if est is None or est.estado == "novo":
        return "teoria"
    if est.estado == "em_revisao":
        return "revisao"
    if est.estado == "em_estudo":
        if _precisa_reforco(est.exposure_count, est.accuracy_rate):
            return "reforco"
        return "questionario"
    # dominado não deve chegar aqui, mas por segurança:
    return "revisao"


# ---------------------------------------------------------------------------
# Cálculo de accuracy_rate a partir de RespostaQuestao
# ---------------------------------------------------------------------------

def _accuracy_from_respostas(
    db: Session, aluno_id: str, subtopico_id: str
) -> tuple[int, float]:
    """
    Retorna (total_respondidas, accuracy_rate) calculados de RespostaQuestao.
    accuracy_rate é 0.0 se nenhuma resposta existe.
    """
    row = (
        db.query(
            sa.func.count(RespostaQuestao.id).label("total"),
            sa.func.sum(
                sa.case((RespostaQuestao.correta == True, 1), else_=0)
            ).label("acertos"),
        )
        .filter(
            RespostaQuestao.aluno_id == aluno_id,
            RespostaQuestao.subtopico_id == subtopico_id,
        )
        .one()
    )
    total = row.total or 0
    acertos = row.acertos or 0
    rate = (acertos / total) if total > 0 else 0.0
    return total, rate


# ---------------------------------------------------------------------------
# Sincronização de estado por subtópico
# ---------------------------------------------------------------------------

def _sincronizar_estados(
    db: Session, aluno_id: str, subtopico_ids: list[str]
) -> dict[str, SubtopicoEstado]:
    """
    Para cada subtópico, calcula accuracy_rate a partir de RespostaQuestao,
    atualiza (ou cria) o registro SubtopicoEstado e recalcula o estado.
    Retorna {subtopico_id: SubtopicoEstado}.
    """
    # Carrega registros existentes em lote
    existentes: dict[str, SubtopicoEstado] = {
        e.subtopico_id: e
        for e in db.query(SubtopicoEstado)
        .filter(
            SubtopicoEstado.aluno_id == aluno_id,
            SubtopicoEstado.subtopico_id.in_(subtopico_ids),
        )
        .all()
    }

    resultado: dict[str, SubtopicoEstado] = {}
    agora = datetime.now(timezone.utc)

    for sub_id in subtopico_ids:
        _total, rate = _accuracy_from_respostas(db, aluno_id, sub_id)

        est = existentes.get(sub_id)
        if est is None:
            est = SubtopicoEstado(
                id=str(uuid.uuid4()),
                aluno_id=aluno_id,
                subtopico_id=sub_id,
                exposure_count=0,
                accuracy_rate=rate,
                estado="novo",
                created_at=agora,
                updated_at=agora,
            )
            db.add(est)
        else:
            est.accuracy_rate = rate
            est.updated_at = agora

        # Recalcula estado (não avança exposure_count aqui — ocorre ao gerar tasks)
        est.estado = _calcular_estado(est.exposure_count, est.accuracy_rate)
        resultado[sub_id] = est

    db.flush()
    return resultado


# ---------------------------------------------------------------------------
# Seleção de questões
# ---------------------------------------------------------------------------

def _selecionar_questoes(
    db: Session, subtopico_id: str, aluno_id: str, quantidade: int
) -> list[str]:
    """
    Retorna até `quantidade` IDs de questões para o subtópico.
    Prioriza questões ainda não respondidas pelo aluno.
    Se insuficientes, preenche com questões já respondidas (as mais antigas).
    """
    if quantidade <= 0:
        return []

    respondidas_ids: set[str] = {
        row[0]
        for row in db.query(RespostaQuestao.questao_id)
        .filter(
            RespostaQuestao.aluno_id == aluno_id,
            RespostaQuestao.subtopico_id == subtopico_id,
        )
        .all()
    }

    todas_ids: list[str] = [
        row[0]
        for row in db.query(Questao.id)
        .filter(Questao.subtopico_id == subtopico_id, Questao.ativo == True)
        .all()
    ]

    unseen = [qid for qid in todas_ids if qid not in respondidas_ids]
    seen = [qid for qid in todas_ids if qid in respondidas_ids]

    random.shuffle(unseen)

    if len(unseen) >= quantidade:
        return unseen[:quantidade]

    needed = quantidade - len(unseen)
    return unseen + seen[:needed]


# ---------------------------------------------------------------------------
# Construção das filas de prioridade
# ---------------------------------------------------------------------------

def _build_priority_queues(
    estados: dict[str, SubtopicoEstado],
    triplas: list[tuple[Topico, Topico, Topico]],
) -> tuple[list, list, list]:
    """
    Retorna (p1, p2, p3) onde cada elemento é (subject, topic, subtopic, estado).

    P1 — revisões pendentes (em_revisao)
    P2 — reforços necessários (em_estudo + abaixo do limiar)
    P3 — novos subtópicos, ordenados por peso_edital DESC
         (inclui em_estudo com accuracy ok → próximo ciclo = questionario)
    """
    p1, p2, p3 = [], [], []

    for subject, topic, subtopic in triplas:
        est = estados.get(subtopic.id)
        estado = est.estado if est else "novo"

        if estado == "dominado":
            continue  # não precisa de task esta semana

        if estado == "em_revisao":
            p1.append((subject, topic, subtopic, est))
        elif estado == "em_estudo":
            if _precisa_reforco(est.exposure_count, est.accuracy_rate):
                p2.append((subject, topic, subtopic, est))
            else:
                # accuracy ok → próximo passo é questionario (P3 por prioridade menor)
                p3.append((subject, topic, subtopic, est))
        else:
            # novo
            p3.append((subject, topic, subtopic, est))

    # P3: novos ordenados por peso_edital DESC; em_estudo-ok mantidos ao final
    def _sort_key(item):
        _, _, subtopic, est = item
        # novos primeiro (peso_edital decrescente), em_estudo-ok depois
        is_novo = (est is None or est.estado == "novo")
        return (0 if is_novo else 1, -(subtopic.peso_edital or 1.0))

    p3.sort(key=_sort_key)
    return p1, p2, p3


# ---------------------------------------------------------------------------
# Construção das tasks
# ---------------------------------------------------------------------------

def _build_tasks(
    db: Session,
    aluno: Aluno,
    meta: Meta,
    tasks_meta: int,
) -> list[StudyTask]:
    """
    Gera a lista de StudyTask para a Meta seguindo as regras pedagógicas.
    """
    area = aluno.area or "fiscal"
    subjects = _subjects_do_ciclo(db, area) or _subjects_fallback(db, area)
    if not subjects:
        return []

    # Mapa subject.id → lista de triplas (subject, topic, subtopic)
    subtopicos_por_subject: dict[str, list] = {}
    todas_triplas: list[tuple[Topico, Topico, Topico]] = []
    for subject in subjects:
        triplas = _subtopicos_da_materia(db, subject)
        if triplas:
            subtopicos_por_subject[subject.id] = triplas
            todas_triplas.extend(triplas)

    if not todas_triplas:
        return []

    # Sincroniza estado de todos os subtópicos
    all_subtopico_ids = [sub.id for (_, _, sub) in todas_triplas]
    estados = _sincronizar_estados(db, aluno.id, all_subtopico_ids)

    # Filas de prioridade globais
    p1, p2, p3 = _build_priority_queues(estados, todas_triplas)
    merged = p1 + p2 + p3

    if not merged:
        raise HTTPException(
            status_code=422,
            detail="Todos os subtópicos foram dominados. Nenhuma task pode ser gerada.",
        )

    # Agrupa merged em deques por subject_id (preservando ordem de prioridade)
    subject_deques: dict[str, deque] = {s.id: deque() for s in subjects}
    for item in merged:
        subject_id = item[0].id
        if subject_id in subject_deques:
            subject_deques[subject_id].append(item)

    # Round-robin entre matérias
    subject_keys = [s.id for s in subjects if subject_deques.get(s.id)]
    tasks_criadas: list[StudyTask] = []
    agora = datetime.now(timezone.utc)
    order = 1

    while len(tasks_criadas) < tasks_meta:
        progrediu = False
        for key in subject_keys:
            if len(tasks_criadas) >= tasks_meta:
                break
            dq = subject_deques.get(key)
            if not dq:
                continue

            subject, topic, subtopic, est = dq.popleft()
            progrediu = True

            tipo = _tipo_task(est)

            # Determina quantidade de questões por tipo
            if tipo == "teoria":
                n_questoes = 5
            elif tipo == "questionario":
                n_questoes = random.randint(20, 30)
            else:  # revisao, reforco
                n_questoes = 10

            questoes_ids = _selecionar_questoes(db, subtopic.id, aluno.id, n_questoes)

            task = StudyTask(
                id=str(uuid.uuid4()),
                aluno_id=aluno.id,
                subject_id=subject.id,
                topic_id=topic.id,
                subtopic_id=subtopic.id,
                tipo=tipo,
                status="pending",
                goal_id=meta.id,
                week_number=meta.numero_semana,
                order_in_week=order,
                questoes_json=json.dumps(questoes_ids) if questoes_ids else None,
                created_at=agora,
            )
            tasks_criadas.append(task)

            # Incrementa exposure_count ao gerar a task (registra exposição)
            if est is not None and tipo in ("teoria", "questionario"):
                est.exposure_count += 1
                est.ultima_exposicao = agora

            order += 1

        if not progrediu:
            break  # todos os deques esgotados

    return tasks_criadas


# ---------------------------------------------------------------------------
# Helpers de guarda
# ---------------------------------------------------------------------------

def _next_semana(db: Session, aluno_id: str) -> int:
    result = (
        db.query(sa.func.max(Meta.numero_semana))
        .filter(Meta.aluno_id == aluno_id)
        .scalar()
    )
    return (result or 0) + 1


def _assert_no_open_meta(db: Session, aluno_id: str) -> None:
    existing = (
        db.query(Meta)
        .filter(Meta.aluno_id == aluno_id, Meta.status == "aberta")
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Já existe uma meta aberta (id={existing.id}, "
                f"semana={existing.numero_semana}). "
                "Encerre-a antes de gerar outra."
            ),
        )


# ---------------------------------------------------------------------------
# Verificação de encerramento automático
# ---------------------------------------------------------------------------

def verificar_encerramento_meta(db: Session, goal_id: str) -> None:
    """
    Chamado após a conclusão de uma task. Atualiza tasks_concluidas e,
    se todas as tasks foram concluídas, encerra a Meta automaticamente.
    """
    meta = db.query(Meta).filter(Meta.id == goal_id).first()
    if not meta or meta.status == "encerrada":
        return

    concluidas = (
        db.query(sa.func.count(StudyTask.id))
        .filter(StudyTask.goal_id == goal_id, StudyTask.status == "completed")
        .scalar()
        or 0
    )
    meta.tasks_concluidas = concluidas
    if meta.tasks_concluidas >= meta.tasks_meta:
        meta.status = "encerrada"
    db.commit()


# ---------------------------------------------------------------------------
# Ponto de entrada principal
# ---------------------------------------------------------------------------

def gerar_meta(db: Session, aluno_id: str) -> Meta:
    """
    Gera uma nova Meta pedagógica com tasks distribuídas por prioridade e
    alternância de matérias para o aluno informado.

    Raises:
        HTTPException 404 — aluno não encontrado
        HTTPException 409 — já existe uma meta aberta para o aluno
        HTTPException 422 — todos os subtópicos dominados (sem tasks a gerar)
    """
    aluno: Optional[Aluno] = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    _assert_no_open_meta(db, aluno_id)

    tasks_meta = max(1, int((aluno.horas_por_dia or 1) * (aluno.dias_por_semana or 1)))
    numero_semana = _next_semana(db, aluno_id)

    meta = Meta(
        id=str(uuid.uuid4()),
        aluno_id=aluno_id,
        numero_semana=numero_semana,
        tasks_meta=tasks_meta,
        tasks_concluidas=0,
        status="aberta",
        created_at=datetime.now(timezone.utc),
    )
    db.add(meta)
    db.flush()  # obtém meta.id sem commit

    tasks = _build_tasks(db, aluno, meta, tasks_meta)

    for task in tasks:
        db.add(task)

    db.commit()
    db.refresh(meta)
    return meta
