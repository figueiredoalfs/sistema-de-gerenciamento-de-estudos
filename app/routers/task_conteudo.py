"""
routers/task_conteudo.py

GET  /task-conteudo/{task_code}               — retorna conteúdo da task
POST /task-conteudo/{task_code}/gerar-pdf     — gera PDF via IA e salva
GET  /task-conteudo/{task_code}/videos        — lista vídeos da task
POST /task-conteudo/{task_code}/videos        — adiciona vídeo manualmente
POST /task-conteudo/{task_code}/videos/buscar — IA busca vídeos e salva
POST /task-videos/{video_id}/avaliar          — avalia um vídeo (nota 1–5)
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.task_conteudo import TaskConteudo
from app.models.task_video import TaskVideo
from app.models.task_video_avaliacao import TaskVideoAvaliacao
from app.schemas.task_conteudo import TaskConteudoPdfResponse, TaskConteudoResponse
from app.schemas.task_video import (
    AvaliarVideoResponse,
    TaskVideoAvaliacaoCreate,
    TaskVideoCreate,
    TaskVideoResponse,
)
from app.services import task_conteudo_service

router = APIRouter(tags=["task-conteudo"])


# ── Helpers ─────────────────────────────────────────────────────────────────────

def _get_conteudo_or_404(task_code: str, db: Session) -> TaskConteudo:
    conteudo = db.query(TaskConteudo).filter(TaskConteudo.task_code == task_code).first()
    if not conteudo:
        raise HTTPException(status_code=404, detail=f"task_code '{task_code}' não encontrado")
    return conteudo


# ── Endpoints: conteúdo ─────────────────────────────────────────────────────────

@router.get("/task-conteudo/{task_code}", response_model=TaskConteudoResponse)
def get_conteudo(
    task_code: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    conteudo = _get_conteudo_or_404(task_code, db)
    if not conteudo.objetivo:
        task_conteudo_service.gerar_objetivo_instrucoes(conteudo, db)
    return conteudo


@router.post("/task-conteudo/{task_code}/gerar-pdf", response_model=TaskConteudoPdfResponse)
def gerar_pdf(
    task_code: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    _get_conteudo_or_404(task_code, db)
    pdf = task_conteudo_service.gerar_pdf(task_code, db)
    return TaskConteudoPdfResponse(task_code=task_code, conteudo_pdf=pdf)


# ── Endpoints: vídeos ───────────────────────────────────────────────────────────

@router.get("/task-conteudo/{task_code}/videos", response_model=List[TaskVideoResponse])
def listar_videos(
    task_code: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    _get_conteudo_or_404(task_code, db)
    return (
        db.query(TaskVideo)
        .filter(TaskVideo.task_code == task_code)
        .order_by(TaskVideo.avaliacao_media.desc())
        .all()
    )


@router.post("/task-conteudo/{task_code}/videos", response_model=TaskVideoResponse, status_code=201)
def adicionar_video(
    task_code: str,
    body: TaskVideoCreate,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    _get_conteudo_or_404(task_code, db)
    video = TaskVideo(task_code=task_code, titulo=body.titulo, url=body.url, descricao=body.descricao)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.post("/task-conteudo/{task_code}/videos/buscar", response_model=List[TaskVideoResponse])
def buscar_videos_ia(
    task_code: str,
    db: Session = Depends(get_db),
    _: Aluno = Depends(get_current_user),
):
    _get_conteudo_or_404(task_code, db)
    return task_conteudo_service.buscar_videos_ia(task_code, db)


# ── Endpoints: avaliação de vídeo ───────────────────────────────────────────────

@router.post("/task-videos/{video_id}/avaliar", response_model=AvaliarVideoResponse)
def avaliar_video(
    video_id: str,
    body: TaskVideoAvaliacaoCreate,
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    video = db.query(TaskVideo).filter(TaskVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    # Upsert da avaliação
    avaliacao = db.query(TaskVideoAvaliacao).filter_by(
        video_id=video_id, aluno_id=usuario.id
    ).first()
    if avaliacao:
        avaliacao.nota = body.nota
    else:
        avaliacao = TaskVideoAvaliacao(video_id=video_id, aluno_id=usuario.id, nota=body.nota)
        db.add(avaliacao)
    db.flush()

    # Recalcular média
    notas = [a.nota for a in db.query(TaskVideoAvaliacao).filter_by(video_id=video_id).all()]
    video.avaliacao_media  = sum(notas) / len(notas)
    video.total_avaliacoes = len(notas)

    db.commit()
    return AvaliarVideoResponse(
        video_id=video_id,
        avaliacao_media=video.avaliacao_media,
        total_avaliacoes=video.total_avaliacoes,
    )
