import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    check_login_rate_limit,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.models.aluno import Aluno
from app.schemas.auth import AlunoCreate, AlunoResponse, AlunoUpdate, AlterarSenhaRequest, TokenResponse

logger = logging.getLogger("skolai.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else "unknown"
    check_login_rate_limit(ip)

    aluno = db.query(Aluno).filter(Aluno.email == form.username, Aluno.ativo == True).first()
    if not aluno or not verify_password(form.password, aluno.senha_hash):
        logger.warning("Login failed for email=%s ip=%s", form.username, ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    logger.info("Login success for aluno_id=%s ip=%s", aluno.id, ip)
    payload = {"sub": aluno.id, "role": aluno.role}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=aluno.role,
        nome=aluno.nome,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    """Troca um refresh token válido por um novo access token."""
    payload = verify_refresh_token(body.refresh_token)
    aluno_id = payload.get("sub")
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.ativo == True).first()
    if not aluno:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    new_payload = {"sub": aluno.id, "role": aluno.role}
    access_token = create_access_token(new_payload)
    refresh_token = create_refresh_token(new_payload)
    logger.info("Token refreshed for aluno_id=%s", aluno.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=aluno.role,
        nome=aluno.nome,
    )


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


@router.patch("/me", response_model=AlunoResponse)
def atualizar_perfil(
    body: AlunoUpdate,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(get_current_user),
):
    """Atualiza campos do perfil do usuário autenticado."""
    NIVEIS_VALIDOS = {"conservador", "moderado", "agressivo"}
    if body.email and body.email != current_user.email:
        if db.query(Aluno).filter(Aluno.email == body.email).first():
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")
        current_user.email = body.email
    if body.nome is not None:
        current_user.nome = body.nome
    if body.nivel_desafio is not None:
        if body.nivel_desafio not in NIVEIS_VALIDOS:
            raise HTTPException(status_code=400, detail=f"nivel_desafio inválido. Use: {NIVEIS_VALIDOS}")
        current_user.nivel_desafio = body.nivel_desafio
    if body.horas_por_dia is not None:
        current_user.horas_por_dia = body.horas_por_dia
    if body.dias_por_semana is not None:
        current_user.dias_por_semana = body.dias_por_semana
    if body.area is not None:
        current_user.area = body.area
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/alterar-senha", status_code=200)
def alterar_senha(
    body: AlterarSenhaRequest,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(get_current_user),
):
    """Altera a senha do usuário autenticado."""
    if not verify_password(body.senha_atual, current_user.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    if len(body.nova_senha) < 6:
        raise HTTPException(status_code=400, detail="A nova senha deve ter pelo menos 6 caracteres")
    current_user.senha_hash = hash_password(body.nova_senha)
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}
