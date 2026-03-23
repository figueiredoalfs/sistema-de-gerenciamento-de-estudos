"""
admin_config.py — Configurações globais do sistema.

GET  /admin/config          — lista todas as configurações
PUT  /admin/config/{chave}  — cria ou atualiza uma configuração
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.config_sistema import ConfigSistema

router = APIRouter(prefix="/admin/config", tags=["admin — configurações"])

MODELOS_IA_DISPONIVEIS = [
    {"value": "gemini-1.5-flash",   "label": "Gemini 1.5 Flash (rápido, barato)"},
    {"value": "gemini-1.5-pro",     "label": "Gemini 1.5 Pro (melhor qualidade)"},
    {"value": "gemini-2.0-flash",   "label": "Gemini 2.0 Flash (mais recente, barato)"},
    {"value": "gemini-2.5-flash",   "label": "Gemini 2.5 Flash (mais caro, thinking)"},
]


class ConfigResponse(BaseModel):
    chave: str
    valor: str
    descricao: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    valor: str
    descricao: Optional[str] = None


@router.get("", response_model=List[ConfigResponse])
def listar_config(
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Lista todas as configurações do sistema."""
    return db.query(ConfigSistema).order_by(ConfigSistema.chave).all()


@router.get("/modelos-ia")
def listar_modelos_ia(
    _: Aluno = Depends(require_admin),
):
    """Retorna os modelos de IA disponíveis para seleção."""
    return MODELOS_IA_DISPONIVEIS


@router.put("/{chave}", response_model=ConfigResponse)
def upsert_config(
    chave: str,
    body: ConfigUpdate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(require_admin),
):
    """Cria ou atualiza uma configuração do sistema."""
    cfg = db.query(ConfigSistema).filter(ConfigSistema.chave == chave).first()
    if cfg:
        cfg.valor = body.valor
        if body.descricao is not None:
            cfg.descricao = body.descricao
        cfg.updated_at = datetime.now(timezone.utc)
    else:
        cfg = ConfigSistema(
            id=str(uuid.uuid4()),
            chave=chave,
            valor=body.valor,
            descricao=body.descricao,
        )
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg
