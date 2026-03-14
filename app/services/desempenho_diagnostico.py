"""
services/desempenho_diagnostico.py

Calcula e persiste o desempenho por subtópico ao concluir uma bateria diagnóstica (Meta 00).
"""

import json
from collections import defaultdict
from typing import List

from sqlalchemy.orm import Session

from app.models.proficiencia import PESO_POR_FONTE, Proficiencia
from app.models.resposta_questao import RespostaQuestao
from app.models.topico import Topico
from app.schemas.resposta_questao import DesempenhoSubtopicoItem


def calcular_e_salvar_desempenho_diagnostico(
    aluno_id: str,
    task,  # StudyTask
    db: Session,
) -> List[DesempenhoSubtopicoItem]:
    """
    Calcula o desempenho por subtópico das questões da bateria diagnóstica e
    persiste como registros de Proficiencia (fonte='calibracao').

    Retorna lista de DesempenhoSubtopicoItem ordenada pela taxa de acerto (mais fraco primeiro).
    """
    if not task.questoes_json:
        return []

    questao_ids: List[str] = json.loads(task.questoes_json)
    if not questao_ids:
        return []

    # Busca todas as respostas do aluno para essas questões
    respostas = (
        db.query(RespostaQuestao)
        .filter(
            RespostaQuestao.aluno_id == aluno_id,
            RespostaQuestao.questao_id.in_(questao_ids),
        )
        .all()
    )

    if not respostas:
        return []

    # Agrupa por subtopico_id
    totais: dict[str, int] = defaultdict(int)
    acertos_map: dict[str, int] = defaultdict(int)
    for r in respostas:
        totais[r.subtopico_id] += 1
        if r.correta:
            acertos_map[r.subtopico_id] += 1

    # Busca nome do subject
    subject = db.query(Topico).filter(Topico.id == task.subject_id).first()
    materia_nome = subject.nome if subject else ""

    peso = PESO_POR_FONTE["calibracao"]  # 1.2
    itens: List[DesempenhoSubtopicoItem] = []

    for subtopico_id, total in totais.items():
        acertos = acertos_map[subtopico_id]
        percentual = round((acertos / total) * 100, 1)

        subtopico = db.query(Topico).filter(Topico.id == subtopico_id).first()
        subtopico_nome = subtopico.nome if subtopico else subtopico_id

        prof = Proficiencia(
            aluno_id=aluno_id,
            topico_id=subtopico_id,
            id_bateria=str(task.id),
            materia=materia_nome,
            subtopico=subtopico_nome,
            acertos=acertos,
            total=total,
            percentual=percentual,
            fonte="calibracao",
            peso_fonte=peso,
        )
        db.add(prof)

        itens.append(
            DesempenhoSubtopicoItem(
                subtopico_id=subtopico_id,
                subtopico_nome=subtopico_nome,
                respondidas=total,
                acertos=acertos,
                taxa_acerto=percentual,
            )
        )

    db.commit()

    # Ordena do mais fraco para o mais forte
    itens.sort(key=lambda x: x.taxa_acerto)
    return itens
