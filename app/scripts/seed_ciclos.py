"""
seed_ciclos.py — popula ciclo_materias com os ciclos básicos pré-definidos.

Idempotente: pula entradas já existentes (mesmo area + subject_id).
Deve ser chamado APÓS seed_topicos, pois depende dos tópicos já existirem.

O ciclo fiscal segue uma ordenação pedagógica:
  1. Base linguística e lógica
  2. Direito fundamental (Constitucional → Administrativo)
  3. Núcleo fiscal (Tributário + Contabilidade)
  4. Administração e finanças públicas
  5. Matérias de apoio
"""

import uuid

from app.core.database import SessionLocal
from app.models.ciclo_materia import CicloMateria
from app.models.topico import Topico
from config_materias import MATERIAS_POR_AREA

# ── Ciclo básico pré-setado — Área Fiscal ─────────────────────────────────────
# Ordem pedagógica: do mais geral ao mais específico.
# O admin pode reorganizar, ativar/desativar ou adicionar matérias pela interface.
CICLO_FISCAL: list[str] = [
    # 1. Base — matérias que alavancam o aprendizado de todas as demais
    "Língua Portuguesa",
    "Raciocínio Lógico-Matemático",

    # 2. Direito fundamental — alicerce para as demais matérias jurídicas
    "Direito Constitucional",
    "Direito Administrativo",

    # 3. Núcleo fiscal — matérias de maior peso nos editais fiscais
    "Direito Tributário",
    "Contabilidade Geral",

    # 4. Gestão e finanças públicas
    "Administração Pública",
    "Administração Financeira e Orçamentária (AFO)",
    "Contabilidade Pública",
    "Lei de Responsabilidade Fiscal (LRF)",
    "Licitações e Contratos",

    # 5. Apoio quantitativo
    "Matemática Financeira",
    "Estatística",

    # 6. Conhecimentos gerais
    "Ética no Serviço Público",
    "Noções de Informática",
    "Redação Oficial",
    "Atualidades",
]

# Ciclos para outras áreas: usa a ordem de MATERIAS_POR_AREA como padrão
CICLOS_PADRAO: dict[str, list[str]] = {
    "fiscal": CICLO_FISCAL,
}


def _get_ciclo(area: str) -> list[str]:
    """Retorna o ciclo pré-definido para a área ou usa MATERIAS_POR_AREA como fallback."""
    return CICLOS_PADRAO.get(area, MATERIAS_POR_AREA.get(area, []))


def seed_ciclos(db=None) -> dict:
    close = db is None
    if db is None:
        db = SessionLocal()

    try:
        # Indexa (area, subject_id) já existentes
        existentes: set[tuple[str, str]] = {
            (c.area, c.subject_id)
            for c in db.query(CicloMateria.area, CicloMateria.subject_id).all()
        }

        total = 0

        for area in MATERIAS_POR_AREA:
            materias = _get_ciclo(area)

            for ordem, materia_nome in enumerate(materias):
                subject = db.query(Topico).filter(
                    Topico.nome == materia_nome,
                    Topico.nivel == 0,
                ).first()

                if not subject:
                    print(f"[AVISO] Tópico nivel=0 não encontrado: '{materia_nome}' (area={area}) — pulando")
                    continue

                if (area, subject.id) in existentes:
                    continue

                db.add(CicloMateria(
                    id=str(uuid.uuid4()),
                    area=area,
                    subject_id=subject.id,
                    ordem=ordem,
                ))
                existentes.add((area, subject.id))
                total += 1

        db.commit()
        print(f"[OK] seed_ciclos: {total} entradas inseridas em ciclo_materias.")
        return {"inseridos": total}

    except Exception as e:
        db.rollback()
        print(f"[ERRO] seed_ciclos falhou: {e}")
        raise
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    seed_ciclos()
