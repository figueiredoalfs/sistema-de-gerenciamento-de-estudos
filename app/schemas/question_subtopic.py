from typing import List

from pydantic import BaseModel


class SubtopicoInfo(BaseModel):
    id: str
    nome: str
    nivel: int

    model_config = {"from_attributes": True}


class AssociarSubtopicoRequest(BaseModel):
    subtopic_ids: List[str]
