"""
routers/dev.py — Endpoints de desenvolvimento/teste.

POST /dev/reset-aluno  — reseta os dados do aluno logado para o estado inicial
                         (útil para testar o fluxo de onboarding do zero)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.aluno import Aluno
from app.models.meta import Meta
from app.models.proficiencia import Proficiencia
from app.models.study_task import StudyTask
from app.models.subtopico_estado import SubtopicoEstado

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/reset-aluno")
def reset_aluno(
    db: Session = Depends(get_db),
    aluno: Aluno = Depends(get_current_user),
):
    """
    Remove todos os dados de progresso do aluno e o devolve ao estado de onboarding.
    USO EXCLUSIVO PARA TESTES DE DESENVOLVIMENTO.
    """
    aluno_id = aluno.id

    # Apaga tasks e metas (tasks têm FK para metas, então tasks primeiro)
    db.query(StudyTask).filter(StudyTask.aluno_id == aluno_id).delete(synchronize_session=False)
    db.query(Meta).filter(Meta.aluno_id == aluno_id).delete(synchronize_session=False)

    # Apaga proficiências e estados de subtópico
    db.query(Proficiencia).filter(Proficiencia.aluno_id == aluno_id).delete(synchronize_session=False)
    db.query(SubtopicoEstado).filter(SubtopicoEstado.aluno_id == aluno_id).delete(synchronize_session=False)

    # Apaga o perfil de estudo (vai ser recriado no onboarding)
    from app.models.perfil_estudo import PerfilEstudo
    db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno_id).delete(synchronize_session=False)

    # Reseta campos do aluno para o estado pré-onboarding
    aluno.area = None
    aluno.banca = None
    aluno.cargo = None
    aluno.data_prova = None
    aluno.diagnostico_pendente = False

    db.commit()
    return {"ok": True, "mensagem": "Dados resetados. Faça o onboarding novamente."}
