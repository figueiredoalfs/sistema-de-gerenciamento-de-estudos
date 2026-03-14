from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    nome: str


class AlunoCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    role: str = "student"


class AlunoResponse(BaseModel):
    id: str
    nome: str
    email: str
    role: str
    nivel_desafio: str
    horas_por_dia: float
    ativo: bool

    model_config = {"from_attributes": True}


class AlunoAdminResponse(BaseModel):
    id: str
    nome: str
    email: str
    role: str
    nivel_desafio: str
    horas_por_dia: float
    dias_por_semana: float
    area: Optional[str]
    ativo: bool
    mentor_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AlunoMentoradoResponse(BaseModel):
    id: str
    nome: str
    email: str
    area: Optional[str]
    nivel_desafio: str
    horas_por_dia: float
    ativo: bool

    model_config = {"from_attributes": True}


class AtribuirMentorRequest(BaseModel):
    mentor_id: Optional[str]
