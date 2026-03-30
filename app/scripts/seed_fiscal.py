"""
seed_fiscal.py — Seed canônico da hierarquia fiscal (Área Fiscal).

Substituição do seed_topicos.py. Executado no startup via lifespan do main.py.

Comportamento:
  1. Para cada matéria em HIERARQUIA, busca topico nivel=0 pelo nome exato.
     Se não existe, cria. Se existe duplicata exata, mantém o com mais filhos
     e re-parenta os filhos do outro, depois desativa o duplicata.
  2. Para matérias que existem com NOME DIFERENTE mas representam a mesma matéria
     canônica (ex: "Contabilidade" → "Contabilidade Geral e Avançada"), renomeia
     para o nome canônico.
  3. Insere módulos (nivel=1) e subtópicos (nivel=2) faltantes.
  4. Desativa topicos nivel=0 cujo nome não está na lista canônica.
  5. Nunca deleta proficiencias — preserva histórico do aluno.

Idempotente: pode ser chamado múltiplas vezes sem efeito colateral.
"""

import uuid

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.topico import Topico
from app.models.proficiencia import Proficiencia
from app.models.ciclo_materia import CicloMateria
from app.scripts.config_materias import HIERARQUIA

# Pesos por matéria canônica
PESO_FISCAL: dict[str, float] = {
    "Direito Tributário":           0.90,
    "Contabilidade Geral e Avançada": 0.85,
    "Direito Administrativo":       0.65,
    "Direito Constitucional":       0.65,
    "Língua Portuguesa":            0.50,
    "Raciocínio Lógico":            0.50,
    "Auditoria":                    0.75,
    "Direito Civil":                0.55,
    "Direito Empresarial":          0.55,
    "Matemática Financeira":        0.70,
    "Tecnologia da Informação":     0.45,
}

# Mapeamento de nomes antigos → nome canônico atual
# Chave: fragmento que pode aparecer no nome antigo (case-insensitive)
# Valor: nome canônico em HIERARQUIA
ALIAS: dict[str, str] = {
    "contabilidade":          "Contabilidade Geral e Avançada",
    "português":              "Língua Portuguesa",
    "lingua portuguesa":      "Língua Portuguesa",
    "informática":            "Tecnologia da Informação",
    "tecnologia da informação": "Tecnologia da Informação",
    "matemática financeira":  "Matemática Financeira",
    "raciocínio lógico":      "Raciocínio Lógico",
    "auditoria":              "Auditoria",
    "direito civil":          "Direito Civil",
    "direito empresarial":    "Direito Empresarial",
    "direito tributário":     "Direito Tributário",
    "direito administrativo": "Direito Administrativo",
    "direito constitucional": "Direito Constitucional",
}

DEFAULT_DECAY = 0.3


def _peso(nome: str) -> float:
    return PESO_FISCAL.get(nome, 0.50)


def _canonico(nome: str) -> str | None:
    """Retorna o nome canônico se o nome antigo for reconhecido pelo alias."""
    nl = nome.lower().strip()
    for alias_frag, canonical in ALIAS.items():
        if alias_frag in nl:
            return canonical
    return None


def seed(db=None) -> dict:
    close = db is None
    if db is None:
        db = SessionLocal()

    try:
        nomes_canonicos = set(HIERARQUIA.keys())

        # ── Passo 1: Normalizar nomes antigos para os canônicos ──────────────
        topicos_raiz = db.query(Topico).filter(Topico.nivel == 0).all()
        for t in topicos_raiz:
            if t.nome in nomes_canonicos:
                continue  # já está correto
            canonical = _canonico(t.nome)
            if canonical and canonical != t.nome:
                # Verificar se já existe um topico com o nome canônico
                existente = db.query(Topico).filter(
                    Topico.nome == canonical, Topico.nivel == 0
                ).first()
                if existente:
                    # Já existe o canônico — re-parenta filhos deste para o canônico
                    db.query(Topico).filter(Topico.parent_id == t.id).update(
                        {"parent_id": existente.id}
                    )
                    db.query(Proficiencia).filter(Proficiencia.topico_id == t.id).update(
                        {"topico_id": existente.id}
                    )
                    db.query(CicloMateria).filter(CicloMateria.subject_id == t.id).update(
                        {"subject_id": existente.id}
                    )
                    t.ativo = False
                    print(f"[seed_fiscal] Mesclado '{t.nome}' → '{canonical}'")
                else:
                    # Renomeia para o nome canônico
                    print(f"[seed_fiscal] Renomeado '{t.nome}' → '{canonical}'")
                    t.nome = canonical
                    t.area = "fiscal"
        db.flush()

        # ── Passo 2: Deduplicar nivel=0 com mesmo nome (pode haver extras) ──
        dupes = (
            db.query(Topico.nome)
            .filter(Topico.nivel == 0, Topico.ativo == True)
            .group_by(Topico.nome)
            .having(func.count(Topico.id) > 1)
            .all()
        )
        for (nome,) in dupes:
            rows = db.query(Topico).filter(
                Topico.nome == nome, Topico.nivel == 0, Topico.ativo == True
            ).all()
            keeper = max(
                rows,
                key=lambda r: db.query(Topico).filter(Topico.parent_id == r.id).count(),
            )
            for r in rows:
                if r.id == keeper.id:
                    continue
                db.query(Topico).filter(Topico.parent_id == r.id).update(
                    {"parent_id": keeper.id}
                )
                db.query(Proficiencia).filter(Proficiencia.topico_id == r.id).update(
                    {"topico_id": keeper.id}
                )
                db.query(CicloMateria).filter(CicloMateria.subject_id == r.id).update(
                    {"subject_id": keeper.id}
                )
                r.ativo = False
                print(f"[seed_fiscal] Duplicata removida: '{nome}' id={r.id}")
        db.flush()

        # ── Passo 3: Inserir matérias, módulos e subtópicos faltantes ────────
        existentes: set[tuple[str, int]] = {
            (t.nome, t.nivel)
            for t in db.query(Topico.nome, Topico.nivel).all()
        }

        materias_criadas = topicos_criados = subtopicos_criados = 0

        for materia, modulos_dict in HIERARQUIA.items():
            peso = _peso(materia)

            if (materia, 0) not in existentes:
                raiz = Topico(
                    id=str(uuid.uuid4()),
                    nome=materia,
                    nivel=0,
                    area="fiscal",
                    decay_rate=DEFAULT_DECAY,
                    peso_edital=peso,
                    ativo=True,
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
                if row:
                    row.ativo = True
                    row.area = "fiscal"
                    if row.peso_edital == 1.0 or row.peso_edital is None:
                        row.peso_edital = peso

            for modulo_nome, subtopicos in modulos_dict.items():
                if (modulo_nome, 1) not in existentes:
                    mod = Topico(
                        id=str(uuid.uuid4()),
                        nome=modulo_nome,
                        nivel=1,
                        area=materia,
                        parent_id=raiz_id,
                        decay_rate=DEFAULT_DECAY,
                        peso_edital=peso,
                    )
                    db.add(mod)
                    db.flush()
                    mod_id = mod.id
                    existentes.add((modulo_nome, 1))
                    topicos_criados += 1
                else:
                    row = db.query(Topico).filter(
                        Topico.nome == modulo_nome, Topico.nivel == 1
                    ).first()
                    mod_id = row.id if row else raiz_id

                for sub in subtopicos:
                    if (sub, 2) not in existentes:
                        db.add(Topico(
                            id=str(uuid.uuid4()),
                            nome=sub,
                            nivel=2,
                            area=materia,
                            parent_id=mod_id,
                            decay_rate=DEFAULT_DECAY,
                            peso_edital=peso,
                        ))
                        existentes.add((sub, 2))
                        subtopicos_criados += 1

        # ── Passo 4: Desativar matérias obsoletas (nivel=0 fora da hierarquia) ─
        db.query(Topico).filter(
            Topico.nivel == 0,
            Topico.nome.notin_(nomes_canonicos),
        ).update({"ativo": False}, synchronize_session="fetch")

        # Garantir area="fiscal" em todos os nivel=0 ativos
        db.query(Topico).filter(Topico.nivel == 0, Topico.ativo == True).update(
            {"area": "fiscal"}, synchronize_session="fetch"
        )

        db.commit()

        print(
            f"[seed_fiscal] Concluído: {materias_criadas} matérias + "
            f"{topicos_criados} módulos + {subtopicos_criados} subtópicos criados."
        )
        return {
            "materias": materias_criadas,
            "topicos": topicos_criados,
            "subtopicos": subtopicos_criados,
        }

    except Exception as e:
        db.rollback()
        print(f"[seed_fiscal] ERRO: {e}")
        raise
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    seed()
