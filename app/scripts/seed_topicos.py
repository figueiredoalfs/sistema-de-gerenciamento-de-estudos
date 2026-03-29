"""
Script de seed: popula a tabela topicos a partir de config_materias.HIERARQUIA.

Uso:
    python -m app.scripts.seed_topicos

Cria (3 níveis com parent_id):
  - nivel=0: matéria raiz (ex: "Direito Tributário")
  - nivel=1: tópico intermediário (ex: "Obrigação Tributária")
  - nivel=2: subtópico folha (ex: "Fato Gerador")

Idempotente: pula registros já existentes (mesmo nome + nivel).
Fonte única de dados: config_materias.HIERARQUIA
"""

import sys
import uuid

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.topico import Topico
from app.models.proficiencia import Proficiencia
from app.models.ciclo_materia import CicloMateria
from app.services.decay import get_decay_rate
from app.scripts.config_materias import HIERARQUIA

# Pesos diferenciados por matéria — base para priorização fiscal
PESO_FISCAL: dict[str, float] = {
    "Direito Tributário":      0.90,
    "Contabilidade":           0.85,
    "Administração":           0.80,
    "Matemática Financeira":   0.70,
    "Direito Constitucional":  0.65,
    "Direito Administrativo":  0.65,
    "Português":               0.50,
    "Raciocínio Lógico":       0.50,
    "Matemática":              0.45,
    "Informática":             0.35,
    "Atualidades":             0.30,
}


def _peso(materia: str) -> float:
    """Retorna peso_edital para a matéria, com fallback de 0.50."""
    for chave, peso in PESO_FISCAL.items():
        if chave.lower() in materia.lower():
            return peso
    return 0.50


def seed(db=None) -> dict:
    close = db is None
    if db is None:
        db = SessionLocal()

    try:
        # ── Deduplicar nivel=0 (matérias raiz) ───────────────────────────────
        dupes_query = (
            db.query(Topico.nome)
            .filter(Topico.nivel == 0)
            .group_by(Topico.nome)
            .having(func.count(Topico.id) > 1)
            .all()
        )
        for (nome,) in dupes_query:
            rows = db.query(Topico).filter(Topico.nome == nome, Topico.nivel == 0).all()
            # Mantém o registro com mais filhos; em empate, usa o mais antigo
            keeper = max(rows, key=lambda r: db.query(Topico).filter(Topico.parent_id == r.id).count())
            for r in rows:
                if r.id == keeper.id:
                    continue
                # Re-parenta filhos (módulos nivel=1)
                db.query(Topico).filter(Topico.parent_id == r.id).update({"parent_id": keeper.id})
                # Re-aponta proficiências
                db.query(Proficiencia).filter(Proficiencia.topico_id == r.id).update({"topico_id": keeper.id})
                # Re-aponta ciclos
                db.query(CicloMateria).filter(CicloMateria.subject_id == r.id).update({"subject_id": keeper.id})
                r.ativo = False
        db.flush()

        # Carrega pares (nome, nivel) já existentes para evitar duplicatas
        existentes: set[tuple[str, int]] = {
            (t.nome, t.nivel)
            for t in db.query(Topico.nome, Topico.nivel).all()
        }

        materias_criadas = 0
        topicos_criados = 0
        subtopicos_criados = 0

        for materia, topicos_dict in HIERARQUIA.items():
            decay = get_decay_rate(materia)
            peso = _peso(materia)

            # ── Nivel 0 — matéria raiz ────────────────────────────────────────
            if (materia, 0) not in existentes:
                raiz = Topico(
                    id=str(uuid.uuid4()),
                    nome=materia,
                    nivel=0,
                    area="fiscal",
                    decay_rate=decay,
                    peso_edital=peso,
                )
                db.add(raiz)
                db.flush()
                raiz_id = raiz.id
                existentes.add((materia, 0))
                materias_criadas += 1
            else:
                row = db.query(Topico).filter(
                    Topico.nome == materia, Topico.nivel == 0
                ).first()
                raiz_id = row.id
                # Atualiza peso se ainda está no default antigo
                if row and row.peso_edital == 1.0:
                    row.peso_edital = peso

            # ── Nivel 1 + 2 — tópicos e subtópicos ───────────────────────────
            for topico_nome, subtopicos in topicos_dict.items():
                if (topico_nome, 1) not in existentes:
                    top = Topico(
                        id=str(uuid.uuid4()),
                        nome=topico_nome,
                        nivel=1,
                        area=materia,
                        parent_id=raiz_id,
                        decay_rate=decay,
                        peso_edital=peso,
                    )
                    db.add(top)
                    db.flush()
                    top_id = top.id
                    existentes.add((topico_nome, 1))
                    topicos_criados += 1
                else:
                    row = db.query(Topico).filter(
                        Topico.nome == topico_nome, Topico.nivel == 1
                    ).first()
                    top_id = row.id if row else raiz_id
                    if row and row.peso_edital == 1.0:
                        row.peso_edital = peso

                for sub in subtopicos:
                    if (sub, 2) not in existentes:
                        db.add(Topico(
                            id=str(uuid.uuid4()),
                            nome=sub,
                            nivel=2,
                            area=materia,
                            parent_id=top_id,
                            decay_rate=decay,
                            peso_edital=peso,
                        ))
                        existentes.add((sub, 2))
                        subtopicos_criados += 1

        # Corrige registros existentes: garante area="fiscal" em todos os nivel=0
        db.query(Topico).filter(Topico.nivel == 0).update({"area": "fiscal"})

        # Desativa matérias nivel=0 cujo nome não está na hierarquia atual
        nomes_ativos = set(HIERARQUIA.keys())
        db.query(Topico).filter(
            Topico.nivel == 0,
            Topico.nome.notin_(nomes_ativos),
        ).update({"ativo": False}, synchronize_session="fetch")

        db.commit()
        resultado = {
            "materias": materias_criadas,
            "topicos": topicos_criados,
            "subtopicos": subtopicos_criados,
        }
        print(
            f"[OK] Seed concluido: {materias_criadas} materias + "
            f"{topicos_criados} topicos + {subtopicos_criados} subtopicos criados."
        )
        return resultado

    except Exception as e:
        db.rollback()
        print(f"[ERRO] Seed falhou: {e}")
        raise
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    seed()
