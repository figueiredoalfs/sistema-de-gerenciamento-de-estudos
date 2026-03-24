from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    role: str
    nome: str


class AlunoCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    codigo_convite: str
    role: str = "estudante"


class AlunoResponse(BaseModel):
    id: str
    nome: str
    email: str
    role: str
    nivel_desafio: str
    horas_por_dia: float
    dias_por_semana: float = 5.0
    area: Optional[str] = None
    ativo: bool
    diagnostico_pendente: bool = False

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


class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    nivel_desafio: Optional[str] = None
    horas_por_dia: Optional[float] = None
    dias_por_semana: Optional[float] = None
    area: Optional[str] = None


class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str


class AlunoAdminUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    area: Optional[str] = None
    role: Optional[str] = None
    horas_por_dia: Optional[float] = None
    dias_por_semana: Optional[float] = None
    nivel_desafio: Optional[str] = None
    mentor_id: Optional[str] = None
    ativo: Optional[bool] = None


class AlunoAdminCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    role: str = "estudante"
