from typing import List, Optional

from pydantic import BaseModel


class SubjectCreate(BaseModel):
    nome: str
    area: Optional[str] = None
    banca: Optional[str] = None
    descricao: Optional[str] = None
    peso_edital: float = 1.0


class TopicCreate(BaseModel):
    nome: str
    subject_id: str
    descricao: Optional[str] = None
    peso_edital: float = 1.0


class SubtopicCreate(BaseModel):
    nome: str
    topic_id: str
    descricao: Optional[str] = None
    decay_rate: float = 0.05
    dependencias_json: str = "[]"


class KnowledgeUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    area: Optional[str] = None
    banca: Optional[str] = None
    peso_edital: Optional[float] = None
    decay_rate: Optional[float] = None
    dependencias_json: Optional[str] = None
    ativo: Optional[bool] = None


class SubtopicResponse(BaseModel):
    id: str
    nome: str
    descricao: Optional[str]
    decay_rate: float
    ativo: bool

    model_config = {"from_attributes": True}


class TopicResponse(BaseModel):
    id: str
    nome: str
    descricao: Optional[str]
    peso_edital: float
    ativo: bool
    subtopics: List[SubtopicResponse] = []

    model_config = {"from_attributes": True}


class SubjectResponse(BaseModel):
    id: str
    nome: str
    area: Optional[str]
    banca: Optional[str]
    descricao: Optional[str]
    peso_edital: float
    ativo: bool
    topics: List[TopicResponse] = []

    model_config = {"from_attributes": True}
