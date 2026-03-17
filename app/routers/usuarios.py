from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin, require_mentor
from app.models.aluno import Aluno
from app.models.proficiencia import Proficiencia
from app.models.sessao import Sessao
from app.schemas.auth import AlunoAdminResponse, AlunoAdminUpdate, AlunoMentoradoResponse, AtribuirMentorRequest

router = APIRouter(tags=["usuários"])


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
    """Admin: ativa/desativa usuário ou altera role."""
    aluno = db.query(Aluno).filter(Aluno.id == usuario_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if aluno.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível alterar o próprio usuário")
    if body.ativo is not None:
        aluno.ativo = body.ativo
    if body.role is not None:
        aluno.role = body.role
    db.commit()
    db.refresh(aluno)
    return aluno


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


@router.get("/mentor/alunos", response_model=List[AlunoMentoradoResponse])
def listar_alunos_mentorados(
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_mentor),
):
    """Mentor: lista seus alunos mentorados. Admin vê todos os alunos com role=student."""
    if current_user.role == "admin":
        return db.query(Aluno).filter(Aluno.role == "student", Aluno.ativo == True).all()
    return current_user.alunos_mentorados
