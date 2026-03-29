from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QuestaoInput(BaseModel):
    materia: str
    subtopico: Optional[str] = None
    topico_id: Optional[str] = None
    acertos: int
    total: int
    fonte: str = "qconcursos"  # qconcursos | tec | prova_anterior_mesma_banca | prova_anterior_outra_banca | simulado | quiz_ia | manual
    banca: Optional[str] = None  # CESPE, FCC, etc.


class BateriaRequest(BaseModel):
    questoes: List[QuestaoInput]
    duracao_min: Optional[int] = None


class ProficienciaOut(BaseModel):
    id: str
    materia: str
    subtopico: Optional[str] = None
    acertos: int
    total: int
    percentual: float
    fonte: str
    peso_fonte: float

    class Config:
        from_attributes = True


class BateriaResponse(BaseModel):
    bateria_id: str
    total_questoes: int
    proficiencias: List[ProficienciaOut]
    mensagem: str


class BateriaResumo(BaseModel):
    bateria_id: str
    data: datetime
    total_questoes: int
    total_acertos: int
    percentual_geral: float
    materias: List[str]


class ProficienciaUpdate(BaseModel):
    id: str
    acertos: int
    total: int


class BateriaUpdate(BaseModel):
    duracao_min: Optional[int] = None
    data: Optional[datetime] = None
    banca: Optional[str] = None
    proficiencias: List[ProficienciaUpdate]


class ProficienciaDetalhe(BaseModel):
    id: str
    materia: str
    subtopico: Optional[str] = None
    acertos: int
    total: int

    class Config:
        from_attributes = True


class BateriaDetalhe(BaseModel):
    bateria_id: str
    data: datetime
    duracao_min: Optional[int] = None
    banca: Optional[str] = None
    fonte: Optional[str] = None
    proficiencias: List[ProficienciaDetalhe]
