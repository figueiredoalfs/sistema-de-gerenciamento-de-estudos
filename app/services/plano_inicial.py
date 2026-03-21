"""
plano_inicial.py — gera as primeiras Sessoes/Tasks do aluno após o onboarding.

Cenários suportados (fase_estudo == "pre_edital"):
  - iniciante:        3 tópicos × 2 subtópicos por matéria → Sessao tipo "teoria_pdf"
  - tempo_de_estudo:  1 StudyTask diagnóstica por matéria, com questões distribuídas
                      entre subtópicos (Meta 00)

Fonte de matérias: tabela ciclo_materias (configurada pelo admin).
Fallback: MATERIAS_POR_AREA de config_materias se o ciclo estiver vazio.
"""

import json
import uuid

from sqlalchemy.orm import Session

from app.models.ciclo_materia import CicloMateria
from app.models.questao import Questao
from app.models.sessao import Sessao
from app.models.study_task import StudyTask
from app.models.topico import Topico

# Número máximo de questões selecionadas por subtópico na bateria diagnóstica
MAX_QUESTOES_POR_SUBTOPICO = 3


def _subjects_do_ciclo(db: Session, area: str) -> list[Topico]:
    """Retorna subjects (nivel=0) ordenados pelo ciclo configurado."""
    ciclos = (
        db.query(CicloMateria)
        .filter(CicloMateria.area == area, CicloMateria.ativo == True)
        .order_by(CicloMateria.ordem)
        .all()
    )
    return [c.subject for c in ciclos if c.subject and c.subject.ativo]


def _subjects_fallback(db: Session, area: str) -> list[Topico]:
    """Fallback: busca todos os subjects ativos da área diretamente do banco."""
    q = db.query(Topico).filter(Topico.nivel == 0, Topico.ativo == True)
    if area:
        q = q.filter(Topico.area == area)
    return q.order_by(Topico.nome).all()


def _selecionar_questoes_diagnostico(db: Session, subject: Topico) -> list[str]:
    """
    Seleciona questões do banco para a bateria diagnóstica de uma matéria.

    Estratégia:
    - Busca todas as questões ativas da matéria
    - Agrupa por subtópico
    - Seleciona até MAX_QUESTOES_POR_SUBTOPICO por subtópico
    - Retorna lista de IDs de questões
    """
    questoes = (
        db.query(Questao)
        .filter(Questao.subject_id == subject.id, Questao.ativo == True)
        .order_by(Questao.subtopic_id)
        .all()
    )

    por_subtopico: dict[str, list[str]] = {}
    for q in questoes:
        chave = q.subtopic_id or "sem_subtopico"
        por_subtopico.setdefault(chave, []).append(q.id)

    selecionadas: list[str] = []
    for ids in por_subtopico.values():
        selecionadas.extend(ids[:MAX_QUESTOES_POR_SUBTOPICO])

    return selecionadas


def _gerar_meta_00_diagnostica(
    db: Session,
    aluno_id: str,
    subjects: list[Topico],
) -> int:
    """
    Gera a Meta 00: uma StudyTask diagnóstica por matéria do ciclo.

    Cada task contém:
    - subject_id: a matéria
    - tipo: "diagnostico"
    - status: "pending"
    - questoes_json: JSON array com IDs das questões selecionadas

    Retorna o número de tasks criadas.
    """
    tasks_criadas = 0

    for subject in subjects:
        questao_ids = _selecionar_questoes_diagnostico(db, subject)

        db.add(StudyTask(
            id=str(uuid.uuid4()),
            aluno_id=aluno_id,
            subject_id=subject.id,
            topic_id=None,
            subtopic_id=None,
            tipo="diagnostico",
            status="pending",
            questoes_json=json.dumps(questao_ids),
        ))
        tasks_criadas += 1

    db.commit()
    return tasks_criadas


def gerar_plano_inicial(
    db: Session,
    aluno_id: str,
    area: str,
    fase_estudo: str,
    experiencia: str,
) -> int:
    """
    Gera as primeiras sessões/tasks para o aluno.
    Retorna o número de itens criados.
    """
    if fase_estudo != "pre_edital":
        return 0

    subjects = _subjects_do_ciclo(db, area) or _subjects_fallback(db, area)

    if experiencia == "iniciante":
        return _gerar_sessoes_iniciante(db, aluno_id, subjects)
    else:
        # tempo_de_estudo → Meta 00 diagnóstica
        return _gerar_meta_00_diagnostica(db, aluno_id, subjects)


def _gerar_sessoes_iniciante(
    db: Session,
    aluno_id: str,
    subjects: list[Topico],
) -> int:
    """Gera sessões de teoria para alunos iniciantes: 3 tópicos × 2 subtópicos por matéria."""
    sessoes_criadas = 0

    for subject in subjects:
        topicos = db.query(Topico).filter(
            Topico.parent_id == subject.id,
            Topico.nivel == 1,
            Topico.ativo == True,
        ).all()

        topicos = topicos[:3]

        for topico in topicos:
            subtopicos = (
                db.query(Topico)
                .filter(
                    Topico.parent_id == topico.id,
                    Topico.nivel == 2,
                    Topico.ativo == True,
                )
                .limit(2)
                .all()
            )

            alvos = subtopicos if subtopicos else [topico]

            for alvo in alvos:
                db.add(Sessao(
                    id=str(uuid.uuid4()),
                    aluno_id=aluno_id,
                    topico_id=alvo.id,
                    tipo="teoria_pdf",
                    duracao_planejada_min=50,
                    confianca="baixa",
                    concluida=False,
                ))
                sessoes_criadas += 1

    db.commit()
    return sessoes_criadas
