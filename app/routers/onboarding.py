"""
POST /onboarding — coleta preferências iniciais e cria o perfil de estudo.

Fluxo:
1. Cria (ou reutiliza) o Aluno
2. Faz upsert do PerfilEstudo com:
   - área do concurso
   - fase de estudo (pre_edital / pos_edital)
   - experiência (iniciante / tempo_de_estudo)
   - disponibilidade (horas_por_dia, dias_por_semana)
   - funcionalidades selecionadas
3. Gera a Meta 01 automaticamente via engine pedagógica
4. Retorna aluno_id, perfil_estudo_id, funcionalidades confirmadas e tasks_geradas
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger("skolai.onboarding")

from app.core.database import get_db
from app.core.security import get_optional_current_user, hash_password
from app.models.aluno import Aluno
from app.models.perfil_estudo import PerfilEstudo
from app.schemas.onboarding import OnboardingRequest, OnboardingResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("", response_model=OnboardingResponse, status_code=201)
def onboarding(
    body: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    # ── 1. Resolver aluno ────────────────────────────────────────────────
    aluno = None

    if current_user:
        aluno = current_user
        aluno.area = body.area
        aluno.horas_por_dia = body.horas_por_dia or 3.0
        aluno.dias_por_semana = body.dias_por_semana or 5.0
        db.flush()
    elif body.email and body.senha and body.nome:
        if db.query(Aluno).filter(Aluno.email == body.email).first():
            raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
        aluno = Aluno(
            nome=body.nome,
            email=body.email,
            senha_hash=hash_password(body.senha),
            area=body.area,
            horas_por_dia=body.horas_por_dia or 3.0,
            dias_por_semana=body.dias_por_semana or 5.0,
        )
        db.add(aluno)
        db.flush()
    else:
        raise HTTPException(
            status_code=400,
            detail="Forneça nome, email e senha para criar a conta no onboarding.",
        )

    # ── 2. Upsert PerfilEstudo ───────────────────────────────────────────
    funcionalidades_json = json.dumps(body.funcionalidades)
    materias_json = json.dumps(body.materias_selecionadas) if body.materias_selecionadas else None

    perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno.id).first()

    if perfil:
        perfil.area = body.area
        perfil.fase_estudo = body.fase_estudo
        perfil.experiencia = body.experiencia
        perfil.tempo_estudo = body.tempo_estudo
        perfil.funcionalidades_json = funcionalidades_json
        perfil.tem_plano_externo = body.tem_plano_externo
        perfil.materias_selecionadas_json = materias_json
        perfil.updated_at = datetime.now(timezone.utc)
    else:
        perfil = PerfilEstudo(
            id=str(uuid.uuid4()),
            aluno_id=aluno.id,
            area=body.area,
            fase_estudo=body.fase_estudo,
            experiencia=body.experiencia,
            tempo_estudo=body.tempo_estudo,
            funcionalidades_json=funcionalidades_json,
            tem_plano_externo=body.tem_plano_externo,
            materias_selecionadas_json=materias_json,
        )
        db.add(perfil)

    try:
        db.commit()
        db.refresh(perfil)
    except Exception as e:
        db.rollback()
        logger.exception("Erro ao salvar onboarding")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar perfil: {str(e)}")

    # Salva os IDs antes de chamar o engine (que pode fazer commit/rollback próprio,
    # expirando os objetos SQLAlchemy e causando lazy-load em estado inválido).
    aluno_id = str(aluno.id)
    perfil_id = str(perfil.id)

    # ── 3. Gerar meta via engine pedagógica ──────────────────────────────
    # Não-iniciantes recebem Meta 00 (diagnóstico) antes da Meta 01.
    # Iniciantes recebem Meta 01 diretamente.
    tasks_geradas = 0
    try:
        from app.services.engine_pedagogica import gerar_meta, gerar_meta_00
        if body.experiencia and body.experiencia != "iniciante":
            meta = gerar_meta_00(db=db, aluno_id=aluno_id)
        else:
            meta = gerar_meta(db=db, aluno_id=aluno_id)
        tasks_geradas = meta.tasks_meta
    except HTTPException:
        # Engine sem ciclo configurado ainda — aluno poderá gerar do Dashboard
        pass
    except Exception:
        logger.exception("Erro ao gerar meta no onboarding (não-bloqueante)")
        db.rollback()

    return OnboardingResponse(
        aluno_id=aluno_id,
        perfil_estudo_id=perfil_id,
        funcionalidades=body.funcionalidades,
        mensagem="Perfil de estudo configurado com sucesso.",
        tasks_geradas=tasks_geradas,
    )
