from typing import List, Optional

from pydantic import BaseModel


class SubtopicoInfo(BaseModel):
    id: str
    nome: str
    nivel: int
    fonte: Optional[str] = None  # "ia" | "manual"

    model_config = {"from_attributes": True}


class AssociarSubtopicoRequest(BaseModel):
    subtopic_ids: List[str]
