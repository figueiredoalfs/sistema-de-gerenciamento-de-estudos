"""
services/plano_pos_diagnostico.py

Gera StudyTasks do tipo 'study' após conclusão de bateria diagnóstica (Meta 00).
"""
import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.study_task import StudyTask
from app.models.topico import Topico
from app.schemas.resposta_questao import DesempenhoSubtopicoItem

LIMIAR_FRAQUEZA = 70.0          # subtópicos abaixo disso recebem task de estudo
MAX_TASKS_POR_DIAGNOSTICO = 10  # limite por conclusão de diagnóstico


def _resolver_hierarquia(
    subtopico_id: str, db: Session
) -> Tuple[Optional[Topico], Optional[Topico], Optional[Topico]]:
    """Dado subtopico_id (nivel=2), retorna (subtopico, topic, subject)."""
    subtopico = db.query(Topico).filter(Topico.id == subtopico_id).first()
    if not subtopico or subtopico.nivel != 2:
        return None, None, None
    topic = db.query(Topico).filter(Topico.id == subtopico.parent_id).first()
    if not topic or topic.nivel != 1:
        return subtopico, None, None
    subject = db.query(Topico).filter(Topico.id == topic.parent_id).first()
    if not subject or subject.nivel != 0:
        return subtopico, topic, None
    return subtopico, topic, subject


def gerar_tasks_pos_diagnostico(
    aluno_id: str,
    desempenho: List[DesempenhoSubtopicoItem],
    db: Session,
) -> List[StudyTask]:
    """
    Gera StudyTasks de estudo para subtópicos fracos identificados no diagnóstico.

    Algoritmo:
    1. Filtra subtópicos com taxa_acerto < LIMIAR_FRAQUEZA (70%)
    2. Resolve hierarquia (subtopico → topic → subject) para cada um
    3. Agrupa por topic; ordena grupos pelo pior desempenho médio (grupo mais fraco primeiro)
    4. Dentro de cada grupo, ordena por taxa_acerto asc (mais fraco primeiro)
    5. Aplica limite MAX_TASKS_POR_DIAGNOSTICO
    6. Cria e persiste StudyTasks com tipo='study', status='pending'

    Retorna lista de StudyTask criadas.
    """
    if not desempenho:
        return []

    fracos = [item for item in desempenho if item.taxa_acerto < LIMIAR_FRAQUEZA]
    if not fracos:
        return []

    # Resolve hierarquia e agrupa por topic
    grupos: dict[str, dict] = {}
    for item in fracos:
        subtopico, topic, subject = _resolver_hierarquia(item.subtopico_id, db)
        if not subtopico or not topic or not subject:
            continue
        if topic.id not in grupos:
            grupos[topic.id] = {"topic": topic, "itens": []}
        grupos[topic.id]["itens"].append((item, subtopico, topic, subject))

    if not grupos:
        return []

    # Ordena grupos por taxa_acerto média (mais fraco primeiro)
    grupos_ordenados = sorted(
        grupos.values(),
        key=lambda g: sum(i[0].taxa_acerto for i in g["itens"]) / len(g["itens"]),
    )

    # Flatten: subtópicos ordenados por fraqueza dentro de cada grupo
    sequencia = []
    for grupo in grupos_ordenados:
        for entry in sorted(grupo["itens"], key=lambda x: x[0].taxa_acerto):
            sequencia.append(entry)

    sequencia = sequencia[:MAX_TASKS_POR_DIAGNOSTICO]

    tasks_criadas: List[StudyTask] = []
    for item, subtopico, topic, subject in sequencia:
        task = StudyTask(
            id=str(uuid.uuid4()),
            aluno_id=aluno_id,
            subject_id=subject.id,
            topic_id=topic.id,
            subtopic_id=subtopico.id,
            tipo="study",
            status="pending",
        )
        db.add(task)
        tasks_criadas.append(task)

    db.commit()
    for t in tasks_criadas:
        db.refresh(t)

    return tasks_criadas
