"""
Script: mescla matérias de informática em uma única "Informática".

Matérias de origem (serão desativadas após o merge):
  - Noções de Informática
  - Engenharia de Software
  - Banco de Dados
  - Redes de Computadores
  - Informática (TI)

O script também:
  - Mescla tópicos (nivel=1) duplicados por nome
  - Mescla subtópicos (nivel=2) duplicados por nome dentro de cada bloco
  - Para questões sem subtópico associado, usa o campo `subject` para criar/vincular

Uso:
    python -m app.scripts.merge_materias_informatica
"""

import sys
import uuid

from sqlalchemy import delete, text
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.models.question_subtopic import QuestionSubtopic
from app.models.questao_banco import QuestaoBanco
from app.models.topico import Topico

NOME_CANONICO = "Informática"

NOMES_ORIGEM = [
    "Noções de Informática",
    "Engenharia de Software",
    "Banco de Dados",
    "Redes de Computadores",
    "Informática (TI)",
]


def _merge_nivel2(db, bloco_id: str) -> None:
    """Mescla subtópicos (nivel=2) duplicados por nome dentro de um bloco."""
    filhos = (
        db.query(Topico)
        .filter(Topico.parent_id == bloco_id, Topico.nivel == 2)
        .order_by(Topico.created_at)
        .all()
    )
    vistos: dict[str, Topico] = {}
    for t in filhos:
        chave = t.nome.strip().lower()
        if chave not in vistos:
            vistos[chave] = t
            continue
        # Duplicata — redirecionar question_subtopics ao sobrevivente
        sobrevivente = vistos[chave]
        duplicatas = (
            db.query(QuestionSubtopic)
            .filter(QuestionSubtopic.subtopic_id == t.id)
            .all()
        )
        for qs in duplicatas:
            existe = db.query(QuestionSubtopic).filter(
                QuestionSubtopic.question_id == qs.question_id,
                QuestionSubtopic.subtopic_id == sobrevivente.id,
            ).first()
            if existe:
                db.delete(qs)
            else:
                qs.subtopic_id = sobrevivente.id
        t.ativo = False
        print(f"    [~] nivel=2 duplicado desativado: '{t.nome}' → '{sobrevivente.nome}'")
    db.flush()


def _merge_nivel1(db, canonical_id: str) -> None:
    """Mescla tópicos (nivel=1) duplicados por nome sob o canônico."""
    blocos = (
        db.query(Topico)
        .filter(Topico.parent_id == canonical_id, Topico.nivel == 1)
        .order_by(Topico.created_at)
        .all()
    )
    vistos: dict[str, Topico] = {}
    for b in blocos:
        chave = b.nome.strip().lower()
        if chave not in vistos:
            vistos[chave] = b
            _merge_nivel2(db, b.id)
            continue
        # Duplicata — reatribuir filhos (nivel=2) ao sobrevivente e desativar
        sobrevivente = vistos[chave]
        filhos = db.query(Topico).filter(Topico.parent_id == b.id, Topico.nivel == 2).all()
        for f in filhos:
            f.parent_id = sobrevivente.id
        db.flush()
        _merge_nivel2(db, sobrevivente.id)
        b.ativo = False
        print(f"  [~] nivel=1 duplicado desativado: '{b.nome}' ({len(filhos)} filhos migrados)")
    db.flush()


def _garantir_bloco_geral(db, canonical_id: str) -> Topico:
    """Retorna ou cria um bloco 'Geral' (nivel=1) sob o canônico."""
    bloco = db.query(Topico).filter(
        Topico.parent_id == canonical_id,
        Topico.nivel == 1,
        Topico.nome.ilike("geral"),
    ).first()
    if not bloco:
        bloco = Topico(id=str(uuid.uuid4()), nivel=1, nome="Geral",
                       parent_id=canonical_id, ativo=True)
        db.add(bloco)
        db.flush()
        print(f"  [+] Bloco 'Geral' criado sob '{NOME_CANONICO}'")
    return bloco


def _vincular_por_subject(db, canonical_id: str) -> None:
    """
    Para questões sem subtópico associado (nivel=2), usa o campo `subject`
    para encontrar ou criar um bloco (nivel=1) e subtópico 'Geral' (nivel=2),
    e cria a associação question_subtopics.
    """
    todos_nomes = [NOME_CANONICO] + NOMES_ORIGEM
    questoes_sem_sub = (
        db.query(QuestaoBanco)
        .filter(QuestaoBanco.materia.in_(todos_nomes))
        .all()
    )

    # Filtrar as que não têm nenhum subtópico associado
    questoes_sem_sub = [
        q for q in questoes_sem_sub
        if not db.query(QuestionSubtopic).filter(
            QuestionSubtopic.question_id == q.id
        ).first()
    ]

    if not questoes_sem_sub:
        print("  [=] Todas as questões já têm subtópico associado")
        return

    print(f"  [i] {len(questoes_sem_sub)} questão(ões) sem subtópico — vinculando por subject")

    # Cache de blocos por nome e seus subtópicos "Geral"
    bloco_cache: dict[str, Topico] = {}
    geral_cache: dict[str, Topico] = {}

    for q in questoes_sem_sub:
        subject = (q.subject or "").strip() or "Geral"

        # Encontrar ou criar bloco nivel=1
        chave = subject.lower()
        if chave not in bloco_cache:
            bloco = db.query(Topico).filter(
                Topico.parent_id == canonical_id,
                Topico.nivel == 1,
                Topico.nome.ilike(subject),
            ).first()
            if not bloco:
                bloco = Topico(id=str(uuid.uuid4()), nivel=1, nome=subject,
                               parent_id=canonical_id, ativo=True)
                db.add(bloco)
                db.flush()
                print(f"    [+] Bloco criado: '{subject}'")
            bloco_cache[chave] = bloco

        bloco = bloco_cache[chave]

        # Encontrar ou criar subtópico "Geral" (nivel=2) sob o bloco
        if bloco.id not in geral_cache:
            geral = db.query(Topico).filter(
                Topico.parent_id == bloco.id,
                Topico.nivel == 2,
                Topico.nome.ilike("geral"),
            ).first()
            if not geral:
                geral = Topico(id=str(uuid.uuid4()), nivel=2, nome="Geral",
                               parent_id=bloco.id, ativo=True)
                db.add(geral)
                db.flush()
                print(f"    [+] Subtópico 'Geral' criado sob '{bloco.nome}'")
            geral_cache[bloco.id] = geral

        geral = geral_cache[bloco.id]

        # Criar associação se não existir
        existe = db.query(QuestionSubtopic).filter(
            QuestionSubtopic.question_id == q.id,
            QuestionSubtopic.subtopic_id == geral.id,
        ).first()
        if not existe:
            db.add(QuestionSubtopic(
                id=str(uuid.uuid4()),
                question_id=q.id,
                subtopic_id=geral.id,
                fonte="auto",
            ))

    db.flush()


def run():
    db = SessionLocal()
    try:
        # 1. Buscar ou criar matéria canônica
        canonico = db.query(Topico).filter(
            Topico.nivel == 0, Topico.nome.ilike(NOME_CANONICO)
        ).first()
        if not canonico:
            canonico = Topico(id=str(uuid.uuid4()), nivel=0, nome=NOME_CANONICO, ativo=True)
            db.add(canonico)
            db.flush()
            print(f"[+] Matéria canônica criada: {NOME_CANONICO}")
        else:
            canonico.ativo = True
            db.flush()
            print(f"[=] Matéria canônica existente: {canonico.nome} (id={canonico.id})")

        # 2. Reatribuir tópicos e questões de cada matéria de origem
        for nome_origem in NOMES_ORIGEM:
            origem = db.query(Topico).filter(
                Topico.nivel == 0, Topico.nome.ilike(nome_origem)
            ).first()
            if not origem:
                print(f"[~] Não encontrada: {nome_origem} — pulando")
                continue
            if origem.id == canonico.id:
                print(f"[~] {nome_origem} já é a matéria canônica — pulando")
                continue

            # Reatribuir tópicos filhos (nivel=1)
            topicos_filhos = db.query(Topico).filter(
                Topico.parent_id == origem.id, Topico.nivel == 1
            ).all()
            for t in topicos_filhos:
                t.parent_id = canonico.id
            print(f"[>] {len(topicos_filhos)} tópico(s) de '{origem.nome}' → '{NOME_CANONICO}'")

            # Atualizar questões
            questoes = db.query(QuestaoBanco).filter(
                QuestaoBanco.materia.ilike(nome_origem)
            ).all()
            for q in questoes:
                q.materia = NOME_CANONICO
            print(f"[>] {len(questoes)} questão(ões) com materia='{nome_origem}' → '{NOME_CANONICO}'")

            # Desativar matéria de origem
            origem.ativo = False
            db.flush()

        # 3. Mesclar tópicos (nivel=1) duplicados e seus subtópicos (nivel=2)
        print(f"\n[i] Mesclando tópicos/subtópicos duplicados sob '{NOME_CANONICO}'...")
        _merge_nivel1(db, canonico.id)

        # 4. Vincular questões sem subtópico usando campo `subject`
        print(f"\n[i] Vinculando questões sem subtópico por subject...")
        _vincular_por_subject(db, canonico.id)

        # 5. Recalcular materia_pendente
        from app.routers.admin_importar_questoes import _calcular_pendente
        questoes_info = db.query(QuestaoBanco).filter(
            QuestaoBanco.materia == NOME_CANONICO
        ).all()
        for q in questoes_info:
            q.materia_pendente = _calcular_pendente(q.materia or "", q.board or "", db)

        db.commit()
        print(f"\n[✓] Merge concluído. {len(questoes_info)} questão(ões) com materia='{NOME_CANONICO}'.")
    except Exception as e:
        db.rollback()
        print(f"[ERRO] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run()
