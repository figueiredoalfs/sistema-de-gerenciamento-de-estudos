from app.core.database import SessionLocal
from app.models.aluno import Aluno
from app.core.security import verify_password
db = SessionLocal()
admin = db.query(Aluno).filter(Aluno.role == 'administrador').first()
if admin:
    print('Email:', admin.email)
    print('Senha SkolaiAdmin2026 bate:', verify_password('SkolaiAdmin2026', admin.senha_hash))
    print('Hash atual:', admin.senha_hash[:30], '...')
else:
    print('Admin nao encontrado')
db.close()
