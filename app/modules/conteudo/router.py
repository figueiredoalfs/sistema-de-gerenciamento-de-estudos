from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.conteudo import service

router = APIRouter(prefix="/conteudo", tags=["conteudo"])


class ConteudoRequest(BaseModel):
    topico: str


class ResumoResponse(BaseModel):
    topico: str
    resumo: str


class FlashcardsResponse(BaseModel):
    topico: str
    flashcards: list[dict]


class ExemploResponse(BaseModel):
    topico: str
    exemplo: str


@router.post("/resumo", response_model=ResumoResponse)
def resumo(body: ConteudoRequest, _=Depends(get_current_user)):
    try:
        texto = service.gerar_resumo(body.topico)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro na IA: {e}")
    return ResumoResponse(topico=body.topico, resumo=texto)


@router.post("/flashcards", response_model=FlashcardsResponse)
def flashcards(body: ConteudoRequest, _=Depends(get_current_user)):
    try:
        cards = service.gerar_flashcards(body.topico)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro na IA: {e}")
    return FlashcardsResponse(topico=body.topico, flashcards=cards)


@router.post("/exemplo", response_model=ExemploResponse)
def exemplo(body: ConteudoRequest, _=Depends(get_current_user)):
    try:
        texto = service.gerar_exemplo(body.topico)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro na IA: {e}")
    return ExemploResponse(topico=body.topico, exemplo=texto)
