"""
Gera sessoes de teste em dev.db para um aluno.
Uso: python -m app.scripts.seed_sessoes_teste <email>

Cria um Cronograma e sessoes para os primeiros 20 topicos do banco.
Util para testar o GET /agenda sem precisar passar pelo onboarding.
"""

import sys
import uuid
from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.models.aluno import Aluno
from app.models.cronograma import Cronograma
from app.models.sessao import Sessao
from app.models.topico import Topico

TIPOS = ["teoria_pdf", "exercicios", "flashcard_texto"]


def seed_sessoes(email: str) -> dict:
    db = SessionLocal()
    try:
        aluno = db.query(Aluno).filter(Aluno.email == email).first()
        if not aluno:
            print(f"[ERRO] Aluno nao encontrado: {email}")
            return {}

        # Remove sessoes antigas
        db.query(Sessao).filter(Sessao.aluno_id == aluno.id).delete()

        # Cria cronograma se nao existir
        cron = db.query(Cronograma).filter(Cronograma.aluno_id == aluno.id, Cronograma.ativo == True).first()
        if not cron:
            cron = Cronograma(id=str(uuid.uuid4()), aluno_id=aluno.id)
            db.add(cron)
            db.flush()

        # Pega os primeiros 20 topicos de nivel 0 e 2
        topicos = db.query(Topico).filter(Topico.ativo == True).limit(20).all()

        agora = datetime.now(timezone.utc)
        count = 0
        for i, topico in enumerate(topicos):
            for tipo in TIPOS:
                duracao = {"teoria_pdf": 50, "exercicios": 45, "flashcard_texto": 20}[tipo]
                sessao = Sessao(
                    id=str(uuid.uuid4()),
                    aluno_id=aluno.id,
                    topico_id=topico.id,
                    cronograma_id=cron.id,
                    tipo=tipo,
                    duracao_planejada_min=duracao,
                    data_agendada=agora + timedelta(days=i),
                    concluida=False,
                )
                db.add(sessao)
                count += 1

        db.commit()
        print(f"[OK] {count} sessoes criadas para {email}")
        return {"sessoes": count, "aluno_id": aluno.id}

    except Exception as e:
        db.rollback()
        print(f"[ERRO] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@aprovai.com"
    seed_sessoes(email)
