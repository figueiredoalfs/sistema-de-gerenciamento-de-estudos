"""
plano_inicial.py — gera as primeiras Sessoes do aluno após o onboarding.

Cenários suportados (fase_estudo == "pre_edital"):
  - iniciante:         3 tópicos × 2 subtópicos por matéria → tipo "teoria_pdf"
  - tempo_de_estudo:   todos os tópicos × 1 subtópico por matéria → tipo "exercicios"

Fonte de matérias: tabela ciclo_materias (configurada pelo admin).
Fallback: MATERIAS_POR_AREA de config_materias se o ciclo estiver vazio.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.ciclo_materia import CicloMateria
from app.models.sessao import Sessao
from app.models.topico import Topico


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
    """Fallback: busca subjects pelo nome usando MATERIAS_POR_AREA."""
    from config_materias import MATERIAS_POR_AREA

    materias = MATERIAS_POR_AREA.get(area, [])
    subjects = []
    for nome in materias:
        s = db.query(Topico).filter(
            Topico.nome == nome, Topico.nivel == 0, Topico.ativo == True
        ).first()
        if s:
            subjects.append(s)
    return subjects


def gerar_plano_inicial(
    db: Session,
    aluno_id: str,
    area: str,
    fase_estudo: str,
    experiencia: str,
) -> int:
    """
    Gera as primeiras Sessoes para o aluno.
    Retorna o número de sessões criadas.
    """
    if fase_estudo != "pre_edital":
        return 0

    subjects = _subjects_do_ciclo(db, area) or _subjects_fallback(db, area)

    if experiencia == "iniciante":
        max_topicos = 3
        max_subtopicos = 2
        tipo_sessao = "teoria_pdf"
    else:
        # tempo_de_estudo → Meta 00 diagnóstica
        max_topicos = None  # todos
        max_subtopicos = 1
        tipo_sessao = "exercicios"

    sessoes_criadas = 0

    for subject in subjects:
        topicos = db.query(Topico).filter(
            Topico.parent_id == subject.id,
            Topico.nivel == 1,
            Topico.ativo == True,
        ).all()

        if max_topicos is not None:
            topicos = topicos[:max_topicos]

        for topico in topicos:
            subtopicos = (
                db.query(Topico)
                .filter(
                    Topico.parent_id == topico.id,
                    Topico.nivel == 2,
                    Topico.ativo == True,
                )
                .limit(max_subtopicos)
                .all()
            )

            # Se não há subtópicos, cria sessão no nível do tópico
            alvos = subtopicos if subtopicos else [topico]

            for alvo in alvos:
                db.add(Sessao(
                    id=str(uuid.uuid4()),
                    aluno_id=aluno_id,
                    topico_id=alvo.id,
                    tipo=tipo_sessao,
                    duracao_planejada_min=50,
                    confianca="baixa",
                    concluida=False,
                ))
                sessoes_criadas += 1

    db.commit()
    return sessoes_criadas
