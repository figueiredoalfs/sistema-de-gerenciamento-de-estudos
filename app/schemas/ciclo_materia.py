from typing import List, Optional

from pydantic import BaseModel


class CicloMateriaCreate(BaseModel):
    area: str
    subject_id: str
    ordem: int = 0


class CicloMateriaUpdate(BaseModel):
    ordem: Optional[int] = None
    ativo: Optional[bool] = None


class CicloMateriaResponse(BaseModel):
    id: str
    area: str
    subject_id: str
    subject_nome: Optional[str] = None
    ordem: int
    ativo: bool

    model_config = {"from_attributes": True}


class CicloMateriaListResponse(BaseModel):
    area: str
    total: int
    itens: List[CicloMateriaResponse]
