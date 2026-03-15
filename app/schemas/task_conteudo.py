from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskConteudoResponse(BaseModel):
    task_code:    str
    subtopico_id: Optional[str] = None
    tipo:         str
    objetivo:     Optional[str] = None
    instrucoes:   Optional[str] = None
    conteudo_pdf: Optional[str] = None
    created_at:   datetime

    model_config = {"from_attributes": True}


class TaskConteudoPdfResponse(BaseModel):
    task_code:    str
    conteudo_pdf: str
