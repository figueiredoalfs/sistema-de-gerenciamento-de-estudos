"""
Script de migração: sisfig.db (SQLite legado) → Skolai (dev.db ou Postgres)

Uso:
    python -m app.scripts.migrar_sisfig <caminho_sisfig.db> <aluno_id>

Mapeamento:
    lancamentos → Proficiencia
    erros       → ErroCritico
    cadastros   → Topico (nivel=2, apenas assuntos únicos)
"""

import sqlite3
import sys
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.erro_critico import ErroCritico
from app.models.proficiencia import PESO_POR_FONTE, Proficiencia
from app.models.topico import Topico
from app.services.decay import get_decay_rate

# Mapeamento de fonte do SISFIG → enum Skolai
FONTE_MAP = {
    "qconcursos": "qconcursos",
    "tec concursos": "tec",
    "tec": "tec",
    "simulado": "simulado",
    "prova anterior": "prova_anterior_outra_banca",
    "prova mesma banca": "prova_anterior_mesma_banca",
    "manual": "manual",
}


def normalizar_fonte(fonte_raw: str) -> str:
    if not fonte_raw:
        return "manual"
    key = fonte_raw.strip().lower()
    for k, v in FONTE_MAP.items():
        if k in key:
            return v
    return "manual"


def migrar(sisfig_path: str, aluno_id: str) -> None:
    print(f"Conectando ao SISFIG: {sisfig_path}")
    src = sqlite3.connect(sisfig_path)
    src.row_factory = sqlite3.Row

    db: Session = SessionLocal()

    try:
        # ── LANCAMENTOS → Proficiencia ────────────────────────────────────
        rows = src.execute("SELECT * FROM lancamentos").fetchall()
        print(f"\nMigrando {len(rows)} lancamentos -> Proficiencia...")

        prof_count = 0
        for row in rows:
            fonte = normalizar_fonte(row["fonte"])
            peso = PESO_POR_FONTE.get(fonte, 1.0)

            data = None
            if row["data"]:
                try:
                    data = datetime.strptime(row["data"], "%Y-%m-%d")
                except ValueError:
                    try:
                        data = datetime.strptime(row["data"], "%d/%m/%Y")
                    except ValueError:
                        data = datetime.now(timezone.utc)

            prof = Proficiencia(
                id=str(uuid.uuid4()),
                aluno_id=aluno_id,
                id_bateria=row["id_bateria"],
                materia=row["materia"],
                subtopico=row["subtopico"],
                acertos=row["acertos"] or 0,
                total=row["total"] or 0,
                percentual=row["percentual"] or 0.0,
                fonte=fonte,
                peso_fonte=peso,
                data=data,
            )
            db.add(prof)
            prof_count += 1

        # ── ERROS → ErroCritico ───────────────────────────────────────────
        rows_erros = src.execute("SELECT * FROM erros").fetchall()
        print(f"Migrando {len(rows_erros)} erros -> ErroCritico...")

        erro_count = 0
        for row in rows_erros:
            data = None
            if row["data"]:
                try:
                    data = datetime.strptime(row["data"], "%Y-%m-%d")
                except ValueError:
                    try:
                        data = datetime.strptime(row["data"], "%d/%m/%Y")
                    except ValueError:
                        data = datetime.now(timezone.utc)

            obs_parts = []
            if row["observacao"]:
                obs_parts.append(row["observacao"])
            if row["providencia"]:
                obs_parts.append(f"Providência: {row['providencia']}")

            erro = ErroCritico(
                id=str(uuid.uuid4()),
                aluno_id=aluno_id,
                id_bateria=row["id_bateria"],
                materia=row["materia"],
                topico_texto=row["topico"],
                qtd_erros=row["qtd_erros"] or 1,
                observacao="\n".join(obs_parts) if obs_parts else None,
                status="pendente",
                data=data,
            )
            db.add(erro)
            erro_count += 1

        # ── CADASTROS → Topico ────────────────────────────────────────────
        rows_cad = src.execute("SELECT * FROM cadastros").fetchall()
        print(f"Migrando {len(rows_cad)} cadastros -> Topico...")

        topico_count = 0
        for row in rows_cad:
            if not row["assunto"]:
                continue
            topico = Topico(
                id=str(uuid.uuid4()),
                nome=row["assunto"],
                nivel=2,
                area=row["materia"],
                decay_rate=get_decay_rate(row["materia"]),
            )
            db.add(topico)
            topico_count += 1

        db.commit()
        print(f"\n[OK] Migracao concluida:")
        print(f"   Proficiencias: {prof_count}")
        print(f"   ErroCritico:   {erro_count}")
        print(f"   Topicos:       {topico_count}")

    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] Migracao falhou: {e}")
        raise
    finally:
        db.close()
        src.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python -m app.scripts.migrar_sisfig <caminho_sisfig.db> <aluno_id>")
        sys.exit(1)

    sisfig_path = sys.argv[1]
    aluno_id = sys.argv[2]
    migrar(sisfig_path, aluno_id)
