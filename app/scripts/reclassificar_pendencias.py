"""
Reclassifica materia_pendente de todas as questões no banco.
Marca como pendente qualquer questão cuja matéria ou banca não esteja cadastrada.
Executa idempotentemente no startup.
"""
from sqlalchemy.orm import Session

from app.models.banca import Banca
from app.models.questao_banco import QuestaoBanco
from app.models.topico import Topico


def _materia_valida(nome: str, db: Session) -> bool:
    if not nome:
        return False
    return (
        db.query(Topico)
        .filter(Topico.nivel == 0, Topico.ativo == True, Topico.nome.ilike(nome.strip()))
        .first()
    ) is not None


def _banca_valida(nome: str, db: Session) -> bool:
    if not nome:
        return True  # sem banca = ok
    return (
        db.query(Banca)
        .filter(Banca.ativo == True, Banca.nome.ilike(nome.strip()))
        .first()
    ) is not None


def reclassificar(db: Session) -> int:
    """
    Percorre todas as questões e atualiza materia_pendente.
    Retorna número de questões atualizadas.
    """
    questoes = db.query(QuestaoBanco).all()
    atualizadas = 0
    for q in questoes:
        mat_ok = _materia_valida(q.materia or "", db)
        ban_ok = _banca_valida(q.board or "", db)
        pendente = not mat_ok or not ban_ok
        if q.materia_pendente != pendente:
            q.materia_pendente = pendente
            atualizadas += 1
    if atualizadas:
        db.commit()
    return atualizadas
