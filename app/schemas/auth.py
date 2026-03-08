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
    role: str = "aluno"


class AlunoResponse(BaseModel):
    id: str
    nome: str
    email: str
    role: str
    nivel_desafio: str
    horas_por_dia: float
    ativo: bool

    model_config = {"from_attributes": True}
