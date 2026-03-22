import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger("skolai.auth")

# ---------------------------------------------------------------------------
# Rate limiting — login (in-memory, sliding window)
# ---------------------------------------------------------------------------
_RATE_WINDOW_SEC = 600   # 10 minutos
_RATE_MAX_ATTEMPTS = 5

_login_attempts: dict[str, list[float]] = defaultdict(list)


def check_login_rate_limit(ip: str) -> None:
    """Levanta 429 se o IP ultrapassou o limite de tentativas de login."""
    now = time.monotonic()
    window_start = now - _RATE_WINDOW_SEC
    _login_attempts[ip] = [t for t in _login_attempts[ip] if t > window_start]
    if len(_login_attempts[ip]) >= _RATE_MAX_ATTEMPTS:
        logger.warning("Rate limit exceeded for IP: %s", ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Aguarde {_RATE_WINDOW_SEC // 60} minutos.",
        )
    _login_attempts[ip].append(now)

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
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_refresh_token(token: str) -> dict:
    """Valida um refresh token e retorna o payload. Levanta 401 se inválido."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido ou expirado")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não é um refresh token")
    return payload


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
