"""
services/gerador_cronograma.py — gera o cronograma semanal de tasks do aluno.

Regra principal:
  tasks_semanais = int(horas_por_dia × dias_por_semana)
  Cada task tem duração padrão de 1 hora e tipo "teoria".

Algoritmo de distribuição:
  - Coleta todos os subtópicos ativos de cada matéria do ciclo do aluno.
  - Distribui as tasks em round-robin entre as matérias para evitar repetição.
  - Cada task recebe week_number e order_in_week.

Fontes:
  - Matérias: tabela ciclo_materias ordenada por campo `ordem` (área do aluno).
  - Fallback: MATERIAS_POR_AREA de config_materias se o ciclo estiver vazio.
  - Subtópicos: tabela topicos (nivel=2, ativo=True).
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.ciclo_materia import CicloMateria
from app.models.study_task import StudyTask
from app.models.topico import Topico


def _subjects_do_ciclo(db: Session, area: str) -> list[Topico]:
    """Retorna subjects (nivel=0) ordenados pelo ciclo configurado para a área."""
    ciclos = (
        db.query(CicloMateria)
        .filter(CicloMateria.area == area, CicloMateria.ativo == True)
        .order_by(CicloMateria.ordem)
        .all()
    )
    return [c.subject for c in ciclos if c.subject and c.subject.ativo]


def _subjects_fallback(db: Session, area: str) -> list[Topico]:
    """Fallback: busca subjects pelo nome usando MATERIAS_POR_AREA."""
    from config_materias import MATERIAS_POR_AREA

    subjects = []
    for nome in MATERIAS_POR_AREA.get(area, []):
        s = db.query(Topico).filter(
            Topico.nome == nome, Topico.nivel == 0, Topico.ativo == True
        ).first()
        if s:
            subjects.append(s)
    return subjects


def _subtopicos_da_materia(
    db: Session, subject: Topico
) -> list[tuple[Topico, Topico, Topico]]:
    """
    Retorna lista de tuplas (subject, topic, subtopic) para todos os subtópicos
    ativos da matéria, percorrendo a hierarquia nivel=1 → nivel=2.
    """
    result = []
    topics = (
        db.query(Topico)
        .filter(
            Topico.parent_id == subject.id,
            Topico.nivel == 1,
            Topico.ativo == True,
        )
        .all()
    )
    for topic in topics:
        subtopics = (
            db.query(Topico)
            .filter(
                Topico.parent_id == topic.id,
                Topico.nivel == 2,
                Topico.ativo == True,
            )
            .all()
        )
        for subtopic in subtopics:
            result.append((subject, topic, subtopic))
    return result


def gerar_cronograma_semanal(
    db: Session,
    aluno_id: str,
    week_number: int = 1,
) -> list[StudyTask]:
    """
    Gera as tasks semanais do aluno com base na disponibilidade informada no onboarding.

    Parâmetros:
      db          — sessão SQLAlchemy
      aluno_id    — ID do aluno
      week_number — número da semana a gerar (padrão: 1)

    Retorna lista de StudyTask criadas (vazia se já existir cronograma para a semana).
    """
    aluno: Optional[Aluno] = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        return []

    # Guard: evita geração duplicada para a mesma semana
    existentes = (
        db.query(StudyTask)
        .filter(
            StudyTask.aluno_id == aluno_id,
            StudyTask.week_number == week_number,
        )
        .first()
    )
    if existentes:
        return []

    tasks_semanais = max(1, int((aluno.horas_por_dia or 1) * (aluno.dias_por_semana or 1)))

    area = aluno.area or "fiscal"
    subjects = _subjects_do_ciclo(db, area) or _subjects_fallback(db, area)
    if not subjects:
        return []

    # Monta filas de (subject, topic, subtopic) por matéria
    filas: list[list[tuple[Topico, Topico, Topico]]] = []
    for subject in subjects:
        subtopicos = _subtopicos_da_materia(db, subject)
        if subtopicos:
            filas.append(subtopicos)

    if not filas:
        return []

    # Round-robin: itera em rodadas pegando 1 subtópico de cada matéria por vez
    tasks_criadas: list[StudyTask] = []
    ponteiros = [0] * len(filas)
    order = 1

    while len(tasks_criadas) < tasks_semanais:
        adicionou_alguma = False
        for idx, fila in enumerate(filas):
            if len(tasks_criadas) >= tasks_semanais:
                break
            ptr = ponteiros[idx]
            if ptr >= len(fila):
                continue  # matéria esgotada nesta rodada
            subject, topic, subtopic = fila[ptr]
            ponteiros[idx] = ptr + 1

            task = StudyTask(
                id=str(uuid.uuid4()),
                aluno_id=aluno_id,
                subject_id=subject.id,
                topic_id=topic.id,
                subtopic_id=subtopic.id,
                tipo="teoria",
                status="pending",
                week_number=week_number,
                order_in_week=order,
            )
            db.add(task)
            tasks_criadas.append(task)
            order += 1
            adicionou_alguma = True

        if not adicionou_alguma:
            break  # todos os subtópicos de todas as matérias foram esgotados

    db.commit()
    for t in tasks_criadas:
        db.refresh(t)

    return tasks_criadas
