"""
Cria um usuário diretamente no banco.

Uso local:
    python -m app.scripts.criar_usuario "Nome" email@x.com senha admin

Uso Railway:
    railway run python -m app.scripts.criar_usuario "Nome" email@x.com senha aluno
"""

import sys

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.aluno import Aluno


def criar(nome: str, email: str, senha: str, role: str = "aluno") -> None:
    db = SessionLocal()
    try:
        if db.query(Aluno).filter(Aluno.email == email).first():
            print(f"❌ E-mail {email} já cadastrado.")
            return
        aluno = Aluno(nome=nome, email=email, senha_hash=hash_password(senha), role=role)
        db.add(aluno)
        db.commit()
        db.refresh(aluno)
        print(f"✅ Usuário criado: {aluno.nome} <{aluno.email}> role={aluno.role} id={aluno.id}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python -m app.scripts.criar_usuario <nome> <email> <senha> [role=aluno]")
        sys.exit(1)
    role = sys.argv[4] if len(sys.argv) > 4 else "aluno"
    criar(sys.argv[1], sys.argv[2], sys.argv[3], role)
