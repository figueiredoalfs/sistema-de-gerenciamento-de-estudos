from typing import List, Optional

from pydantic import BaseModel


class AreaInfo(BaseModel):
    id: str
    nome: str
    ativo: bool = True
    fonte: Optional[str] = None  # "ia" | "manual" (presente apenas nas associações)

    model_config = {"from_attributes": True}


class AssociarAreaRequest(BaseModel):
    area_ids: List[str]
