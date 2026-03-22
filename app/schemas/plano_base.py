from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FasePlano(BaseModel):
    numero: int
    nome: str
    materias: List[str] = []
    materias_novas: List[str] = []
    # campos legados — aceitos mas ignorados na geração nova
    criterio_avanco: Optional[str] = None
    subtopicos: List[str] = []
    subtopicos_novos: List[str] = []


class PlanoBaseCreate(BaseModel):
    area: str
    perfil: str  # iniciante | intermediario | avancado
    fases: List[FasePlano]


class PlanoBaseUpdate(BaseModel):
    # conteudo = estrutura completa {fases, ordem_subtopicos, prerequisitos}
    conteudo: Optional[Dict[str, Any]] = None
    # fases = legado, aceito para compatibilidade
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
