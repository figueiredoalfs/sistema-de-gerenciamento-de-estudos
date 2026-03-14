from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin, require_mentor
from app.models.aluno import Aluno
from app.schemas.auth import AlunoAdminResponse, AlunoMentoradoResponse, AtribuirMentorRequest

router = APIRouter(tags=["usuários"])


@router.get("/admin/usuarios", response_model=List[AlunoAdminResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_admin),
):
    """Admin: lista todos os usuários cadastrados."""
    return db.query(Aluno).order_by(Aluno.created_at.desc()).all()


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


@router.get("/mentor/alunos", response_model=List[AlunoMentoradoResponse])
def listar_alunos_mentorados(
    db: Session = Depends(get_db),
    current_user: Aluno = Depends(require_mentor),
):
    """Mentor: lista seus alunos mentorados. Admin vê todos os alunos com role=student."""
    if current_user.role == "admin":
        return db.query(Aluno).filter(Aluno.role == "student", Aluno.ativo == True).all()
    return current_user.alunos_mentorados
