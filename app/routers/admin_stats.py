"""
admin_stats.py — endpoints de estatísticas e listagem para o painel admin.

GET /admin/stats   — métricas gerais do sistema
GET /admin/alunos  — lista de alunos com resumo
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.aluno import Aluno
from app.models.ciclo_materia import CicloMateria
from app.models.perfil_estudo import PerfilEstudo
from app.models.sessao import Sessao
from app.models.topico import Topico

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    total_alunos  = db.query(Aluno).filter(Aluno.role == "aluno").count()
    total_sessoes = db.query(Sessao).count()
    total_ciclos  = db.query(CicloMateria).filter(CicloMateria.ativo == True).count()
    total_topicos = db.query(Topico).count()

    return {
        "total_alunos":  total_alunos,
        "total_sessoes": total_sessoes,
        "total_ciclos":  total_ciclos,
        "total_topicos": total_topicos,
    }


@router.get("/alunos")
def listar_alunos(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    alunos = db.query(Aluno).filter(Aluno.role == "aluno").order_by(Aluno.nome).all()

    itens = []
    for a in alunos:
        perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == a.id).first()
        total_sessoes = db.query(Sessao).filter(Sessao.aluno_id == a.id).count()
        itens.append({
            "id":           a.id,
            "nome":         a.nome,
            "email":        a.email,
            "area":         perfil.area         if perfil else "—",
            "experiencia":  perfil.experiencia  if perfil else "—",
            "total_sessoes": total_sessoes,
        })

    return {"total": len(itens), "itens": itens}
