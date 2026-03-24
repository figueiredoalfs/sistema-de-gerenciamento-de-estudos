"""
app/scripts/seed_bancas.py
Garante que as bancas examinadoras padrão existem no banco.
Idempotente — pula bancas já cadastradas (compara por nome, case-insensitive).
"""

import uuid
from app.core.database import SessionLocal
from app.models.banca import Banca

# (nome, ativo)
BANCAS_PADRAO = [
    ("AMAUC", True),
    ("AMEOSC", True),
    ("AOCP", True),
    ("APLICATIVA", True),
    ("AVANÇASP", True),
    ("BANCA DESCONHECIDA", True),
    ("CCMPM", True),
    ("CEBRASPE (CESPE)", True),
    ("CEPERJ", True),
    ("CESPE/CEBRASP", False),
    ("CETAP", True),
    ("CETRO", True),
    ("CONSESP", True),
    ("CONSULPLAN", False),
    ("CONSULTEC", True),
    ("CONTEMAX", True),
    ("COTEC FADENOR", True),
    ("CPCON UEPB", True),
    ("CSC IFPA", True),
    ("Com. Exam.", True),
    ("Com. Org.", True),
    ("DIRECTA", True),
    ("DIRENS Aeronáutica", True),
    ("EDUCA PB", True),
    ("EPL Concursos", True),
    ("ESAF", True),
    ("ESAG", True),
    ("FACAPE", True),
    ("FACET", True),
    ("FAFIPA", True),
    ("FAPTO", True),
    ("FAU UNICENTRO", True),
    ("FAUEL", True),
    ("FCC", True),
    ("FEPESE", True),
    ("FGV", True),
    ("FUMARC", True),
    ("FUNATEC", True),
    ("FUNDATEC", True),
    ("FUNDEP", True),
    ("FUNDEPES COPEVE-UFAL", True),
    ("FURB", True),
    ("Fênix Instituto", True),
    ("GAMA", True),
    ("IADES", True),
    ("IAUPE", True),
    ("IBADE", True),
    ("IBAM", True),
    ("IBFC", True),
    ("IDCAP", True),
    ("IDECAN", True),
    ("IDESG", True),
    ("IDHTEC", True),
    ("IDIB", True),
    ("IESES", True),
    ("IGECAP", True),
    ("IGECS", True),
    ("IGEDUC", True),
    ("INAZ do Pará", True),
    ("INCAB", True),
    ("INSTITUTO CIDADES", True),
    ("ISBA", True),
    ("ITAME", True),
    ("Ibest", True),
    ("Instituto ACCESS", True),
    ("Instituto CONSULPAM", True),
    ("Instituto Consulplan", True),
    ("Instituto Darwin", True),
    ("Instituto Excelência", True),
    ("Instituto IACP", True),
    ("Instituto JK", True),
    ("Instituto SECPLAN", True),
    ("Instituto Verbena", True),
    ("Instituto Ágata", True),
    ("LJ Assessoria", True),
    ("Legalle", True),
    ("Marinha", True),
    ("NC UFPR", True),
    ("OBJETIVA CONCURSOS", True),
    ("OMNI", True),
    ("PRÓ-MUNICÍPIO", True),
    ("PUC PR", True),
    ("PaqTc-PB", True),
    ("QUADRIX", True),
    ("SELECON", True),
    ("SMA-RJ", True),
    ("UEPA", True),
    ("UNESC", True),
    ("UNIVALI", True),
    ("Unifil", True),
    ("VUNESP", True),
    ("Ápice", True),
]


def seed_bancas() -> None:
    db = SessionLocal()
    try:
        # Carrega nomes já cadastrados (lower-case para comparação)
        existentes = {b.nome.lower() for b in db.query(Banca.nome).all()}
        novas = [
            Banca(id=str(uuid.uuid4()), nome=nome, ativo=ativo)
            for nome, ativo in BANCAS_PADRAO
            if nome.lower() not in existentes
        ]
        if novas:
            db.bulk_save_objects(novas)
            db.commit()
    finally:
        db.close()
