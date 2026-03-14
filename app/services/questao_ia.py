"""
Stub do serviço de geração de questões pela IA.

Este módulo será usado futuramente por workers de diagnóstico e avaliação.
A fonte das questões criadas aqui é sempre fixada em "ia".
"""
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session


def criar_questao_ia(
    subtopic_id: str,
    subject_id: str,
    topic_id: str,
    enunciado: str,
    alternativas: dict,
    resposta_correta: str,
    db: Session,
    banca: str | None = None,
    ano: int | None = None,
):
    """
    Cria uma questão com fonte='ia' no banco de dados.

    Deve ser chamada por workers ou serviços de IA, nunca diretamente via endpoint público.

    Args:
        subtopic_id: ID do subtópico (nivel=2)
        subject_id: ID da matéria (nivel=0)
        topic_id: ID do tópico (nivel=1)
        enunciado: Texto da questão
        alternativas: Dict com chaves A-E e os textos das alternativas
        resposta_correta: Uma das letras A, B, C, D ou E
        db: Sessão do banco de dados
        banca: Banca do concurso (opcional)
        ano: Ano da questão (opcional)

    Returns:
        Instância de Questao persistida no banco
    """
    from app.models.questao import Questao

    questao = Questao(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        topic_id=topic_id,
        subtopic_id=subtopic_id,
        enunciado=enunciado,
        alternativas_json=json.dumps(alternativas, ensure_ascii=False),
        resposta_correta=resposta_correta,
        fonte="ia",
        banca=banca,
        ano=ano,
        created_at=datetime.now(timezone.utc),
    )
    db.add(questao)
    db.commit()
    db.refresh(questao)
    return questao
