from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    from app.models.aluno import Aluno

    payload = _decode_token(token)
    aluno_id: str = payload.get("sub")
    if not aluno_id:
        raise HTTPException(status_code=401, detail="Token sem subject")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.ativo == True).first()
    if not aluno:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return aluno


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


def require_mentor(current_user=Depends(get_current_user)):
    if current_user.role not in ("mentor", "administrador"):
        raise HTTPException(status_code=403, detail="Acesso restrito a mentores")
    return current_user


def get_optional_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)),
    db: Session = Depends(get_db),
):
    """Retorna o aluno autenticado ou None se não houver token válido."""
    if not token:
        return None
    from app.models.aluno import Aluno
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        aluno_id: str = payload.get("sub")
        if not aluno_id:
            return None
        return db.query(Aluno).filter(Aluno.id == aluno_id, Aluno.ativo == True).first()
    except JWTError:
        return None
