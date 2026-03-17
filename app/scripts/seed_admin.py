"""
app/scripts/seed_admin.py
Garante que existe pelo menos 1 usuário admin no banco FastAPI (dev.db).
Chamado automaticamente no startup do servidor — idempotente.

Credenciais configuradas em Settings (lidas do .env):
  ADMIN_EMAIL  (padrão: admin@skolai.com)
  ADMIN_SENHA  (padrão: admin123)
  ADMIN_NOME   (padrão: Admin)
"""

import uuid

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.aluno import Aluno
from app.core.security import hash_password

ADMIN_EMAIL = settings.ADMIN_EMAIL
ADMIN_SENHA = settings.ADMIN_SENHA
ADMIN_NOME  = settings.ADMIN_NOME


def seed_admin() -> None:
    db = SessionLocal()
    try:
        # Migra roles antigas (idempotente)
        db.query(Aluno).filter(Aluno.role == "admin").update({"role": "administrador"})
        db.query(Aluno).filter(Aluno.role == "student").update({"role": "estudante"})
        db.commit()

        # Remove emails admin legados
        for old_email in ("admin@concursoai.com", "admin@aprovai.com", "admin@skolai.com"):
            legado = db.query(Aluno).filter(Aluno.email == old_email).first()
            if legado:
                db.delete(legado)
        db.commit()

        existe = db.query(Aluno).filter(Aluno.email == ADMIN_EMAIL).first()
        if not existe:
            db.add(Aluno(
                id=str(uuid.uuid4()),
                nome=ADMIN_NOME,
                email=ADMIN_EMAIL,
                senha_hash=hash_password(ADMIN_SENHA),
                role="administrador",
                ativo=True,
            ))
            db.commit()
    finally:
        db.close()
