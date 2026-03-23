"""
plano_base_aluno.py — Endpoints de PlanoBase para o aluno autenticado.

GET  /plano-base/meu  — retorna o PlanoBase ativo do aluno
                        Se não existir, dispara geração via IA (admin revisa)
                        e retorna 202 enquanto processa.
"""
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.perfil_estudo import PerfilEstudo
from app.models.plano_base import PlanoBase

router = APIRouter(prefix="/plano-base", tags=["plano base"])


def _experiencia_para_perfil(experiencia: str, tempo_estudo: Optional[str]) -> str:
    """Mapeia experiencia + tempo_estudo do PerfilEstudo para o perfil do PlanoBase."""
    if not experiencia or experiencia == "iniciante":
        return "iniciante"
    # tempo_de_estudo
    if tempo_estudo in ("<1m", "1-3m"):
        return "iniciante"
    if tempo_estudo == "3-6m":
        return "intermediario"
    return "avancado"


class FasePlano(BaseModel):
    numero: int
    nome: str
    criterio_avanco: Optional[str] = None
    materias: List[str] = []


class PlanoBaseAlunoResponse(BaseModel):
    id: str
    area: str
    perfil: str
    versao: int
    gerado_por_ia: bool
    revisado_admin: bool
    fases: List[FasePlano]
    fase_atual: int
    status: str  # "ativo" | "gerando" | "sem_plano"


@router.get("/meu", response_model=PlanoBaseAlunoResponse)
def meu_plano(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    Retorna o PlanoBase ativo do aluno.
    Busca na ordem:
      1. perfil_estudo.plano_base_id (plano associado diretamente)
      2. PlanoBase ativo para area + perfil do aluno
      3. Se não existe: dispara geração via IA e retorna status='gerando'
    """
    perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == usuario.id).first()
    area = (perfil.area if perfil else None) or usuario.area or "outro"
    perfil_nome = _experiencia_para_perfil(
        perfil.experiencia if perfil else None,
        perfil.tempo_estudo if perfil else None,
    )
    fase_atual = perfil.fase_atual if perfil else 1

    # 1. Plano associado diretamente ao perfil
    plano = None
    if perfil and perfil.plano_base_id:
        plano = db.query(PlanoBase).filter(
            PlanoBase.id == perfil.plano_base_id,
            PlanoBase.ativo == True,
        ).first()

    # 2. Plano ativo para area + perfil
    if not plano:
        plano = db.query(PlanoBase).filter(
            PlanoBase.area == area,
            PlanoBase.perfil == perfil_nome,
            PlanoBase.ativo == True,
            PlanoBase.revisado_admin == True,
        ).order_by(PlanoBase.versao.desc()).first()

    # 3. Qualquer plano ativo para a área (independente de revisão)
    if not plano:
        plano = db.query(PlanoBase).filter(
            PlanoBase.area == area,
            PlanoBase.ativo == True,
        ).order_by(PlanoBase.versao.desc()).first()

    if plano:
        try:
            fases_raw = json.loads(plano.fases_json or "[]")
        except (ValueError, TypeError):
            fases_raw = []
        fases = [FasePlano(**f) if isinstance(f, dict) else FasePlano(numero=i+1, nome=str(f)) for i, f in enumerate(fases_raw)]
        return PlanoBaseAlunoResponse(
            id=plano.id,
            area=plano.area,
            perfil=plano.perfil,
            versao=plano.versao,
            gerado_por_ia=plano.gerado_por_ia,
            revisado_admin=plano.revisado_admin,
            fases=fases,
            fase_atual=fase_atual,
            status="ativo",
        )

    # 4. Nenhum plano — disparar geração assíncrona via IA
    _disparar_geracao_plano(db, area, perfil_nome)

    return PlanoBaseAlunoResponse(
        id="",
        area=area,
        perfil=perfil_nome,
        versao=0,
        gerado_por_ia=True,
        revisado_admin=False,
        fases=[],
        fase_atual=fase_atual,
        status="gerando",
    )


def _disparar_geracao_plano(db: Session, area: str, perfil: str):
    """Gera PlanoBase via IA se ainda não existe um pendente."""
    ja_existe = db.query(PlanoBase).filter(
        PlanoBase.area == area,
        PlanoBase.perfil == perfil,
        PlanoBase.ativo == True,
    ).first()
    if ja_existe:
        return

    try:
        from app.core.ai_provider import get_ai_provider
        from app.services.gerar_plano_base import gerar_plano_via_ia

        ai = get_ai_provider(db)
        fases_json = gerar_plano_via_ia(ai=ai, area=area, perfil=perfil, db=db)

        plano = PlanoBase(
            id=str(uuid.uuid4()),
            area=area,
            perfil=perfil,
            versao=1,
            gerado_por_ia=True,
            revisado_admin=False,
            ativo=True,
            fases_json=fases_json,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(plano)
        db.commit()
    except Exception:
        pass  # Não bloqueia o aluno — admin gerará manualmente
