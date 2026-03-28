import logging
from datetime import datetime, timezone
from typing import List, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger("skolai.usuarios")
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin, require_mentor, hash_password
from app.models.aluno import Aluno
from app.models.perfil_estudo import PerfilEstudo
from app.models.proficiencia import Proficiencia
from app.models.resposta_questao import RespostaQuestao
from app.models.sessao import Sessao
from app.schemas.auth import AlunoAdminResponse, AlunoAdminUpdate, AlunoMentoradoResponse, AtribuirMentorRequest, AlunoAdminCreate

router = APIRouter(tags=["usuários"])


@router.post("/admin/usuarios", response_model=AlunoAdminResponse, status_code=201)
def criar_usuario(
    body: AlunoAdminCreate,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: cria um novo usuário com qualquer role."""
    if db.query(Aluno).filter(Aluno.email == body.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    import uuid
    aluno = Aluno(
        id=str(uuid.uuid4()),
        nome=body.nome,
        email=body.email,
        senha_hash=hash_password(body.password),
        role=body.role,
        ativo=True,
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


@router.get("/admin/usuarios", response_model=List[AlunoAdminResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: lista todos os usuários cadastrados."""
    return db.query(Aluno).order_by(Aluno.created_at.desc()).all()


@router.patch("/admin/usuarios/{usuario_id}", response_model=AlunoAdminResponse)
def atualizar_usuario(
    usuario_id: str,
    body: AlunoAdminUpdate,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: edita dados completos de um usuário."""
    aluno = db.query(Aluno).filter(Aluno.id == usuario_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if aluno.id == current_user.id and body.ativo is False:
        raise HTTPException(status_code=400, detail="Não é possível desativar o próprio usuário")

    if body.nome is not None:
        aluno.nome = body.nome
    if body.email is not None and body.email != aluno.email:
        if db.query(Aluno).filter(Aluno.email == body.email).first():
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")
        aluno.email = body.email
    if body.area is not None:
        aluno.area = body.area
    if body.role is not None:
        aluno.role = body.role
    if body.horas_por_dia is not None:
        aluno.horas_por_dia = body.horas_por_dia
    if body.dias_por_semana is not None:
        aluno.dias_por_semana = body.dias_por_semana
    if body.nivel_desafio is not None:
        aluno.nivel_desafio = body.nivel_desafio
    if body.mentor_id is not None:
        mentor = db.query(Aluno).filter(Aluno.id == body.mentor_id, Aluno.role == "mentor").first()
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor não encontrado")
        aluno.mentor_id = body.mentor_id
    if "mentor_id" in body.model_fields_set and body.mentor_id is None:
        aluno.mentor_id = None
    if body.ativo is not None:
        aluno.ativo = body.ativo

    db.commit()
    db.refresh(aluno)
    return aluno


@router.post("/admin/usuarios/{usuario_id}/reset-senha")
def reset_senha_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: gera senha temporária para o usuário (8 chars alfanuméricos)."""
    import secrets
    import string

    aluno = db.query(Aluno).filter(Aluno.id == usuario_id).first()
    if not aluno:
        logger.warning("reset-senha: usuário não encontrado. usuario_id=%r", usuario_id)
        raise HTTPException(status_code=404, detail=f"Usuário não encontrado (id={usuario_id})")

    alphabet = string.ascii_letters + string.digits
    senha_temp = "".join(secrets.choice(alphabet) for _ in range(8))
    aluno.senha_hash = hash_password(senha_temp)
    db.commit()
    return {"senha_temporaria": senha_temp, "mensagem": "Senha redefinida. Informe ao usuário para trocar no primeiro acesso."}


@router.patch("/admin/usuarios/{usuario_id}/mentor", response_model=AlunoAdminResponse)
def atribuir_mentor(
    usuario_id: str,
    body: AtribuirMentorRequest,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: atribui ou remove mentor de um aluno."""
    aluno = db.query(Aluno).filter(Aluno.id == usuario_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if body.mentor_id is not None:
        mentor = db.query(Aluno).filter(
            Aluno.id == body.mentor_id, Aluno.role == "mentor"
        ).first()
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor não encontrado")
        if body.mentor_id == usuario_id:
            raise HTTPException(status_code=400, detail="Usuário não pode ser mentor de si mesmo")

    aluno.mentor_id = body.mentor_id
    db.commit()
    db.refresh(aluno)
    return aluno


@router.get("/admin/usuarios/{usuario_id}/progresso")
def progresso_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: retorna métricas de desempenho de um usuário específico."""
    aluno = db.query(Aluno).filter(Aluno.id == usuario_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    registros = db.query(Proficiencia).filter(Proficiencia.aluno_id == usuario_id).all()
    total_sessoes = db.query(Sessao).filter(Sessao.aluno_id == usuario_id).count()

    agrup: dict = {}
    for r in registros:
        mat = r.materia or "Sem matéria"
        if mat not in agrup:
            agrup[mat] = {"acertos": 0, "total": 0}
        agrup[mat]["acertos"] += r.acertos or 0
        agrup[mat]["total"] += r.total or 0

    total_q = sum(v["total"] for v in agrup.values())
    total_a = sum(v["acertos"] for v in agrup.values())

    def perc(a, t):
        return round(a / t * 100, 1) if t > 0 else 0.0

    por_materia = sorted(
        [
            {"materia": m, "realizadas": v["total"], "acertos": v["acertos"], "perc": perc(v["acertos"], v["total"])}
            for m, v in agrup.items()
        ],
        key=lambda x: -x["perc"],
    )

    return {
        "total_questoes": total_q,
        "total_acertos": total_a,
        "perc_geral": perc(total_a, total_q),
        "total_sessoes": total_sessoes,
        "por_materia": por_materia,
    }


@router.get("/mentor/alunos/{aluno_id}/progresso")
def progresso_aluno_mentor(
    aluno_id: str,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_mentor),
):
    """Mentor: retorna métricas de desempenho de um aluno mentorado."""
    # Mentor só pode ver seus próprios alunos; admin pode ver qualquer um
    if current_user.role != "administrador":
        ids_mentorados = [a.id for a in current_user.alunos_mentorados]
        if aluno_id not in ids_mentorados:
            raise HTTPException(status_code=403, detail="Aluno não pertence ao seu grupo de mentoreados")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    registros = db.query(Proficiencia).filter(Proficiencia.aluno_id == aluno_id).all()
    total_sessoes = db.query(Sessao).filter(Sessao.aluno_id == aluno_id).count()

    agrup: dict = {}
    for r in registros:
        mat = r.materia or "Sem matéria"
        if mat not in agrup:
            agrup[mat] = {"acertos": 0, "total": 0}
        agrup[mat]["acertos"] += r.acertos or 0
        agrup[mat]["total"] += r.total or 0

    total_q = sum(v["total"] for v in agrup.values())
    total_a = sum(v["acertos"] for v in agrup.values())

    def perc(a, t):
        return round(a / t * 100, 1) if t > 0 else 0.0

    por_materia = sorted(
        [
            {"materia": m, "realizadas": v["total"], "acertos": v["acertos"], "perc": perc(v["acertos"], v["total"])}
            for m, v in agrup.items()
        ],
        key=lambda x: -x["perc"],
    )

    return {
        "nome": aluno.nome,
        "total_questoes": total_q,
        "total_acertos": total_a,
        "perc_geral": perc(total_a, total_q),
        "total_sessoes": total_sessoes,
        "por_materia": por_materia,
    }


@router.get("/mentor/alunos/{aluno_id}/resumo")
def resumo_aluno_mentor(
    aluno_id: str,
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_mentor),
):
    """Mentor: retorna resumo detalhado de um aluno mentorado (fase, meta, pontos fortes/fracos)."""
    if current_user.role != "administrador":
        ids_mentorados = [a.id for a in current_user.alunos_mentorados]
        if aluno_id not in ids_mentorados:
            raise HTTPException(status_code=403, detail="Aluno não pertence ao seu grupo de mentoreados")

    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    def perc(a, t):
        return round(a / t * 100, 1) if t > 0 else 0.0

    # Fase do plano e perfil
    perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno_id).first()
    fase_atual = perfil.fase_atual if perfil else None
    experiencia = perfil.experiencia if perfil else None

    meta_info = None

    # Última atividade (última resposta)
    ultima_resposta = (
        db.query(RespostaQuestao.respondida_em)
        .filter(RespostaQuestao.aluno_id == aluno_id)
        .order_by(RespostaQuestao.respondida_em.desc())
        .first()
    )
    ultima_atividade = ultima_resposta[0] if ultima_resposta else None

    # Desempenho por matéria via Proficiencia
    registros = db.query(Proficiencia).filter(Proficiencia.aluno_id == aluno_id).all()
    agrup: dict = {}
    for r in registros:
        mat = r.materia or "Sem matéria"
        if mat not in agrup:
            agrup[mat] = {"acertos": 0, "total": 0}
        agrup[mat]["acertos"] += r.acertos or 0
        agrup[mat]["total"] += r.total or 0

    total_q = sum(v["total"] for v in agrup.values())
    total_a = sum(v["acertos"] for v in agrup.values())

    por_materia = sorted(
        [
            {"materia": m, "realizadas": v["total"], "acertos": v["acertos"], "perc": perc(v["acertos"], v["total"])}
            for m, v in agrup.items()
            if v["total"] > 0
        ],
        key=lambda x: -x["perc"],
    )

    pontos_fortes = [m for m in por_materia if m["perc"] >= 70][:3]
    pontos_fracos = sorted([m for m in por_materia if m["perc"] < 50], key=lambda x: x["perc"])[:3]

    return {
        "aluno_id": aluno_id,
        "nome": aluno.nome,
        "email": aluno.email,
        "area": aluno.area,
        "ativo": aluno.ativo,
        "fase_atual": fase_atual,
        "experiencia": experiencia,
        "diagnostico_pendente": aluno.diagnostico_pendente,
        "meta_ativa": meta_info,
        "ultima_atividade": ultima_atividade,
        "desempenho": {
            "total_questoes": total_q,
            "total_acertos": total_a,
            "perc_geral": perc(total_a, total_q),
        },
        "pontos_fortes": pontos_fortes,
        "pontos_fracos": pontos_fracos,
        "por_materia": por_materia,
    }


@router.get("/mentor/alunos", response_model=List[AlunoMentoradoResponse])
def listar_alunos_mentorados(
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_mentor),
):
    """Mentor: lista seus alunos mentorados. Admin vê todos os alunos com role=student."""
    if current_user.role == "admin":
        return db.query(Aluno).filter(Aluno.role == "student", Aluno.ativo == True).all()
    return current_user.alunos_mentorados
