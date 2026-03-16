"""
routers/dev.py — Endpoints temporários para desenvolvimento/testes.
REMOVER antes do deploy em produção.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.meta import Meta
from app.models.perfil_estudo import PerfilEstudo
from app.models.proficiencia import Proficiencia
from app.models.resposta_questao import RespostaQuestao
from app.models.sessao import Sessao
from app.models.study_task import StudyTask
from app.models.subtopico_estado import SubtopicoEstado

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/reset-aluno")
def reset_aluno(
    db: Session = Depends(get_db),
    usuario: Aluno = Depends(get_current_user),
):
    """
    [DEV] Apaga todos os dados de estudo do aluno logado e reinicia o estado do zero,
    incluindo perfil de estudo. O aluno será redirecionado para o onboarding.
    """
    aluno_id = usuario.id

    # Ordem importa: deletar filhos antes dos pais para evitar FK violations.
    db.query(SubtopicoEstado).filter(SubtopicoEstado.aluno_id == aluno_id).delete(synchronize_session=False)
    db.query(RespostaQuestao).filter(RespostaQuestao.aluno_id == aluno_id).delete(synchronize_session=False)
    db.query(Proficiencia).filter(Proficiencia.aluno_id == aluno_id).delete(synchronize_session=False)
    db.query(Sessao).filter(Sessao.aluno_id == aluno_id).delete(synchronize_session=False)
    # StudyTask antes de Meta (FK goal_id → metas.id)
    db.query(StudyTask).filter(StudyTask.aluno_id == aluno_id).delete(synchronize_session=False)
    db.query(Meta).filter(Meta.aluno_id == aluno_id).delete(synchronize_session=False)
    # PerfilEstudo — removido para forçar re-onboarding
    db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno_id).delete(synchronize_session=False)

    # Limpa campo area do aluno (trigger do OnboardingGuard no frontend)
    # e reseta disponibilidade para defaults
    db.query(Aluno).filter(Aluno.id == aluno_id).update(
        {
            "area": None,
            "banca": None,
            "cargo": None,
            "data_prova": None,
            "horas_por_dia": 3.0,
            "dias_por_semana": 5.0,
            "diagnostico_pendente": True,
        },
        synchronize_session=False,
    )
    db.commit()

    return {"ok": True, "mensagem": "Dados resetados. Redirecionando para o onboarding."}
