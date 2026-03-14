"""
app/scripts/seed_admin.py
Garante que existe pelo menos 1 usuário no banco FastAPI (dev.db).
Chamado automaticamente no startup do servidor — idempotente.

Credenciais padrão sobrescritas por variáveis de ambiente:
  ADMIN_EMAIL  (padrão: admin@concursoai.com)
  ADMIN_SENHA  (padrão: admin123)
  ADMIN_NOME   (padrão: Admin)
"""

import os
import uuid

from app.core.database import SessionLocal
from app.models.aluno import Aluno
from app.core.security import hash_password

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@concursoai.com")
ADMIN_SENHA = os.getenv("ADMIN_SENHA", "admin123")
ADMIN_NOME  = os.getenv("ADMIN_NOME",  "Admin")


def seed_admin() -> None:
    db = SessionLocal()
    try:
        existe = db.query(Aluno).filter(Aluno.email == ADMIN_EMAIL).first()
        if not existe:
            db.add(Aluno(
                id=str(uuid.uuid4()),
                nome=ADMIN_NOME,
                email=ADMIN_EMAIL,
                senha_hash=hash_password(ADMIN_SENHA),
                role="admin",
                ativo=True,
            ))
            db.commit()
    finally:
        db.close()
