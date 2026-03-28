"""
Lista usuários e/ou redefine senha.

Listar todos:
    railway run python scripts/reset_senha.py

Redefinir senha:
    railway run python scripts/reset_senha.py email@x.com nova_senha

Local:
    python scripts/reset_senha.py
    python scripts/reset_senha.py admin@skolai.com admin123
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.aluno import Aluno


def listar():
    db = SessionLocal()
    try:
        alunos = db.query(Aluno).order_by(Aluno.created_at).all()
        if not alunos:
            print("Nenhum usuário encontrado.")
            return
        print(f"{'ID':36}  {'Email':40}  {'Role':15}  {'Ativo'}")
        print("-" * 100)
        for a in alunos:
            print(f"{a.id}  {a.email:40}  {a.role:15}  {a.ativo}")
    finally:
        db.close()


def reset(email: str, nova_senha: str):
    db = SessionLocal()
    try:
        aluno = db.query(Aluno).filter(Aluno.email == email).first()
        if not aluno:
            print(f"❌ Usuário não encontrado: {email}")
            return
        aluno.senha_hash = hash_password(nova_senha)
        aluno.ativo = True
        db.commit()
        print(f"✅ Senha redefinida para {email} (role={aluno.role}, ativo={aluno.ativo})")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        listar()
    elif len(sys.argv) == 3:
        reset(sys.argv[1], sys.argv[2])
    else:
        print("Uso: python scripts/reset_senha.py [email nova_senha]")
        sys.exit(1)
