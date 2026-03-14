from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

FonteQuestao = Literal["ia", "admin", "qconcursos", "tec", "prova_real", "simulado"]
RespostaCorreta = Literal["A", "B", "C", "D", "E"]

# Fontes que o admin pode selecionar manualmente (IA é reservado para criação automática)
FONTES_ADMIN = {"admin", "qconcursos", "tec", "prova_real", "simulado"}


class AlternativasSchema(BaseModel):
    A: str
    B: str
    C: str
    D: str
    E: str


class QuestaoCreate(BaseModel):
    subject_id: str
    topic_id: str
    subtopic_id: str
    enunciado: str
    alternativas: AlternativasSchema
    resposta_correta: RespostaCorreta
    fonte: FonteQuestao = "admin"
    banca: Optional[str] = None
    ano: Optional[int] = None


class QuestaoIACreate(BaseModel):
    """Schema interno usado pelo serviço de IA. A fonte é fixada em 'ia' no código."""
    subject_id: str
    topic_id: str
    subtopic_id: str
    enunciado: str
    alternativas: AlternativasSchema
    resposta_correta: RespostaCorreta
    banca: Optional[str] = None
    ano: Optional[int] = None


class QuestaoUpdate(BaseModel):
    enunciado: Optional[str] = None
    alternativas: Optional[AlternativasSchema] = None
    resposta_correta: Optional[RespostaCorreta] = None
    fonte: Optional[FonteQuestao] = None
    banca: Optional[str] = None
    ano: Optional[int] = None
    ativo: Optional[bool] = None


class QuestaoResponse(BaseModel):
    id: str
    subject_id: str
    topic_id: str
    subtopic_id: str
    enunciado: str
    alternativas_json: str
    resposta_correta: str
    fonte: str
    banca: Optional[str]
    ano: Optional[int]
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}
