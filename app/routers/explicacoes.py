"""
Endpoints de explicações automáticas de subtópicos.

GET /explicacoes/topico/{topico_id}
  — Retorna explicação em cache ou gera via IA (primeira chamada).
  — Compartilhada por todos os alunos; não depende do usuário logado.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.services.explicacao_subtopico import obter_ou_gerar

router = APIRouter(prefix="/explicacoes", tags=["explicações"])


class ExplicacaoResponse(BaseModel):
    topico_id: str
    content: str
    cached: bool


@router.get("/topico/{topico_id}", response_model=ExplicacaoResponse)
def get_explicacao(
    topico_id: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    """
    Retorna a explicação do subtópico.
    - Se já estiver em cache: resposta imediata (cached=true).
    - Se não existir: gera via Gemini, salva e retorna (cached=false).
    """
    try:
        content, cached = obter_ou_gerar(topico_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar explicação: {str(e)}",
        )

    if not content:
        raise HTTPException(status_code=404, detail="Tópico não encontrado.")

    return ExplicacaoResponse(topico_id=topico_id, content=content, cached=cached)
