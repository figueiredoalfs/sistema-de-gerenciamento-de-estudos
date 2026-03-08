from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.aluno import Aluno
from app.schemas.auth import AlunoCreate, AlunoResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(Aluno.email == form.username, Aluno.ativo == True).first()
    if not aluno or not verify_password(form.password, aluno.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )
    token = create_access_token({"sub": aluno.id, "role": aluno.role})
    return TokenResponse(access_token=token, role=aluno.role, nome=aluno.nome)


@router.post("/register", response_model=AlunoResponse, status_code=201)
def register(body: AlunoCreate, db: Session = Depends(get_db)):
    if db.query(Aluno).filter(Aluno.email == body.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    aluno = Aluno(
        nome=body.nome,
        email=body.email,
        senha_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


@router.get("/me", response_model=AlunoResponse)
def me(current_user: Aluno = Depends(get_current_user)):
    return current_user
