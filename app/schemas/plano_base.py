from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class FasePlano(BaseModel):
    numero: int
    nome: str
    criterio_avanco: str
    materias: List[str]


class PlanoBaseCreate(BaseModel):
    area: str
    perfil: str  # iniciante | intermediario | avancado
    fases: List[FasePlano]


class PlanoBaseUpdate(BaseModel):
    fases: Optional[List[FasePlano]] = None
    revisado_admin: Optional[bool] = None
    ativo: Optional[bool] = None


class PlanoBaseResponse(BaseModel):
    id: str
    area: str
    perfil: str
    versao: int
    gerado_por_ia: bool
    revisado_admin: bool
    ativo: bool
    fases_json: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class GerarPlanoRequest(BaseModel):
    area: str
    perfil: str  # iniciante | intermediario | avancado
