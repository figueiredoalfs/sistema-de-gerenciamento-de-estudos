from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

from app.schemas.question_subtopic import SubtopicoInfo

RespostaCorreta = Literal["A", "B", "C", "D", "E"]


class AlternativasImport(BaseModel):
    A: str
    B: str
    C: str
    D: str
    E: str


class QuestaoImportItem(BaseModel):
    subject: str
    board: Optional[str] = None
    year: Optional[int] = None
    statement: str
    alternatives: AlternativasImport
    correct_answer: RespostaCorreta


class ImportacaoRequest(BaseModel):
    disciplina_sigla: str
    questoes: List[QuestaoImportItem]


class ImportacaoResponse(BaseModel):
    importadas: int
    erros: List[str]


class QuestaoBancoResponse(BaseModel):
    id: str
    question_code: str
    subject: str
    statement: str
    alternatives_json: str
    correct_answer: str
    board: Optional[str]
    year: Optional[int]
    created_at: datetime
    subtopicos: List[SubtopicoInfo] = []

    model_config = {"from_attributes": True}
