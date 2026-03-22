"""
Script de seed: popula a tabela areas com as áreas padrão do sistema.
Idempotente — pula áreas já existentes (mesmo nome).
"""
import uuid

from app.core.database import SessionLocal
from app.models.area import Area

_AREAS_PADRAO = [
    "fiscal",
    "eaof_com",
    "eaof_svm",
    "cfoe_com",
    "juridica",
    "policial",
    "ti",
    "saude",
    "outro",
]


def seed_areas(db=None) -> dict:
    close = db is None
    if db is None:
        db = SessionLocal()

    try:
        existentes = {a.nome for a in db.query(Area.nome).all()}
        criadas = 0
        for nome in _AREAS_PADRAO:
            if nome not in existentes:
                db.add(Area(id=str(uuid.uuid4()), nome=nome, ativo=True))
                criadas += 1
        if criadas:
            db.commit()
        return {"criadas": criadas, "ja_existiam": len(_AREAS_PADRAO) - criadas}
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    resultado = seed_areas()
    print(f"Áreas criadas: {resultado['criadas']} | Já existiam: {resultado['ja_existiam']}")
