"""
POST /onboarding — coleta preferências iniciais e cria o perfil de estudo.

Fluxo:
1. Cria (ou reutiliza) o Aluno
2. Faz upsert do PerfilEstudo com:
   - área do concurso
   - fase de estudo (pre_edital / pos_edital)
   - experiência (iniciante / tempo_de_estudo)
   - funcionalidades selecionadas
3. Retorna aluno_id, perfil_estudo_id e funcionalidades confirmadas
"""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
        db.flush()
    elif body.email and body.senha and body.nome:
        if db.query(Aluno).filter(Aluno.email == body.email).first():
            raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
        aluno = Aluno(
            nome=body.nome,
            email=body.email,
            senha_hash=hash_password(body.senha),
            area=body.area,
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

    perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno.id).first()

    if perfil:
        # Atualiza perfil existente
        perfil.area = body.area
        perfil.fase_estudo = body.fase_estudo
        perfil.experiencia = body.experiencia
        perfil.tempo_estudo = body.tempo_estudo
        perfil.funcionalidades_json = funcionalidades_json
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
        )
        db.add(perfil)

    db.commit()
    db.refresh(perfil)

    return OnboardingResponse(
        aluno_id=aluno.id,
        perfil_estudo_id=perfil.id,
        funcionalidades=body.funcionalidades,
        mensagem="Perfil de estudo configurado com sucesso.",
    )
