"""
app/services/avancar_fase.py — Lógica de avanço de fase no PlanoBase.

Verifica se um aluno atingiu o critério de avanço da sua fase atual e,
se positivo, avança para a próxima fase no PerfilEstudo.

O critério padrão adotado é: média de acertos nas matérias da fase >= 70%.
O texto do campo 'criterio_avanco' é descritivo; a lógica quantitativa
usa o limiar THRESHOLD_ACERTOS.
"""
import json

from sqlalchemy.orm import Session

from app.models.perfil_estudo import PerfilEstudo
from app.models.plano_base import PlanoBase
from app.models.proficiencia import Proficiencia

THRESHOLD_ACERTOS = 70.0  # % mínimo para avançar de fase


def _perc(acertos: int, total: int) -> float:
    return round(acertos / total * 100, 1) if total > 0 else 0.0


def _media_acertos_materias(aluno_id: str, materias: list[str], db: Session) -> float:
    """Calcula a média de % de acertos do aluno nas matérias da fase."""
    if not materias:
        return 0.0

    resultados = []
    for materia in materias:
        registros = (
            db.query(Proficiencia)
            .filter(
                Proficiencia.aluno_id == aluno_id,
                Proficiencia.materia.ilike(f"%{materia}%"),
            )
            .all()
        )
        total = sum(r.total or 0 for r in registros)
        acertos = sum(r.acertos or 0 for r in registros)
        if total > 0:
            resultados.append(_perc(acertos, total))

    if not resultados:
        return 0.0
    return round(sum(resultados) / len(resultados), 1)


def verificar_e_avancar(aluno_id: str, db: Session) -> dict:
    """
    Verifica se o aluno deve avançar de fase com base no PlanoBase associado.

    Retorna um dict com:
      - avancou (bool)
      - fase_anterior (int)
      - fase_atual (int)
      - media_acertos (float)
      - mensagem (str)
    """
    perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno_id).first()
    if not perfil or not perfil.plano_base_id:
        return {"avancou": False, "mensagem": "Aluno sem PlanoBase associado."}

    plano = db.query(PlanoBase).filter(PlanoBase.id == perfil.plano_base_id).first()
    if not plano:
        return {"avancou": False, "mensagem": "PlanoBase não encontrado."}

    try:
        fases = json.loads(plano.fases_json)
    except (json.JSONDecodeError, TypeError):
        return {"avancou": False, "mensagem": "PlanoBase com fases inválidas."}

    fase_atual_num = perfil.fase_atual or 1
    fase_idx = next((i for i, f in enumerate(fases) if f.get("numero") == fase_atual_num), None)

    if fase_idx is None:
        return {"avancou": False, "mensagem": f"Fase {fase_atual_num} não encontrada no plano."}

    # Se já está na última fase
    if fase_idx >= len(fases) - 1:
        return {
            "avancou": False,
            "fase_anterior": fase_atual_num,
            "fase_atual": fase_atual_num,
            "mensagem": "Aluno já está na última fase do plano.",
        }

    fase = fases[fase_idx]
    materias = fase.get("materias", [])
    media = _media_acertos_materias(aluno_id, materias, db)

    if media < THRESHOLD_ACERTOS:
        return {
            "avancou": False,
            "fase_anterior": fase_atual_num,
            "fase_atual": fase_atual_num,
            "media_acertos": media,
            "mensagem": f"Média de acertos {media}% abaixo do limiar {THRESHOLD_ACERTOS}%.",
        }

    proxima_fase = fases[fase_idx + 1]
    perfil.fase_atual = proxima_fase["numero"]
    db.commit()

    return {
        "avancou": True,
        "fase_anterior": fase_atual_num,
        "fase_atual": proxima_fase["numero"],
        "media_acertos": media,
        "mensagem": f"Avançou para a fase {proxima_fase['numero']}: {proxima_fase.get('nome', '')}.",
    }


def associar_plano_base(aluno_id: str, plano_base_id: str, db: Session) -> bool:
    """Associa um PlanoBase ao perfil do aluno e redefine para fase 1."""
    perfil = db.query(PerfilEstudo).filter(PerfilEstudo.aluno_id == aluno_id).first()
    if not perfil:
        return False
    perfil.plano_base_id = plano_base_id
    perfil.fase_atual = 1
    db.commit()
    return True
