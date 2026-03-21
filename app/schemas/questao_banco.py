from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, field_validator

from app.schemas.question_area import AreaInfo
from app.schemas.question_subtopic import SubtopicoInfo

RespostaCorreta = Literal["A", "B", "C", "D", "E"]

_GABARITO_MAP = {
    "A": "A", "B": "B", "C": "C", "D": "D", "E": "E",
    "CERTO": "C", "ERRADO": "E",
    "CERTA": "C", "ERRADA": "E",
}


class AlternativasImport(BaseModel):
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = None
    E: Optional[str] = None


class QuestaoImportItem(BaseModel):
    materia: str              # disciplina — usado para gerar o question_code
    subject: str              # assunto específico da questão
    board: Optional[str] = None
    year: Optional[int] = None
    statement: str
    alternatives: Optional[AlternativasImport] = None
    correct_answer: str

    @field_validator("correct_answer")
    @classmethod
    def normalizar_gabarito(cls, v: str) -> str:
        normalizado = _GABARITO_MAP.get(str(v).strip().upper())
        if not normalizado:
            raise ValueError(
                f'Gabarito inválido: "{v}". Use A–E, CERTO ou ERRADO.'
            )
        return normalizado


class ImportacaoRequest(BaseModel):
    questoes: List[Any]  # validação individual no endpoint para isolar erros por questão
    classificar_subtopicos: bool = False  # True para classificar subtópicos via IA após import
    classificar_areas: bool = False        # True para classificar áreas via IA após import


class ImportacaoResponse(BaseModel):
    importadas: int
    erros: List[str]
    avisos_ia: List[str] = []


class QuestaoUpdateRequest(BaseModel):
    materia: Optional[str] = None
    subject: Optional[str] = None
    statement: Optional[str] = None
    alternatives: Optional[AlternativasImport] = None
    correct_answer: Optional[RespostaCorreta] = None
    board: Optional[str] = None
    year: Optional[int] = None
    materia_pendente: Optional[bool] = None


class QuestaoBancoResponse(BaseModel):
    id: str
    question_code: str
    materia: Optional[str] = None
    subject: str
    statement: str
    alternatives_json: str
    correct_answer: str
    board: Optional[str]
    year: Optional[int]
    materia_pendente: bool = False
    created_at: datetime
    subtopicos: List[SubtopicoInfo] = []
    areas: List[AreaInfo] = []

    model_config = {"from_attributes": True}
