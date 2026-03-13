"""
POST /onboarding — orquestra o fluxo completo das 5 telas.

Fluxo:
1. Cria (ou reutiliza) o Aluno
2. Cria o Cronograma com as preferências
3. Perfil B → estima nível inicial por matéria
   Perfil C → importa CSV Qconcursos/TEC → popula Proficiencia
4. Gera sessões multimodais por tópico conforme peso
5. Cria MetaSemanal inicial
6. Retorna cronograma gerado (aluno vê valor imediato)
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_optional_current_user, hash_password
from app.models.aluno import Aluno
from app.models.cronograma import Cronograma
from app.models.meta_semanal import MetaSemanal
from app.models.proficiencia import PESO_POR_FONTE, Proficiencia
from app.models.sessao import Sessao
from app.models.topico import Topico
from app.schemas.onboarding import OnboardingRequest, OnboardingResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# Nível inicial por tempo declarado (Perfil B)
NIVEL_POR_TEMPO = {
    "<1m": "basico",
    "1-3m": "intermediario",
    "3-6m": "avancado",
    ">6m": "expert",
}

# Percentual estimado por nível (âncora para a calibração adaptativa)
# Fase 1: 5 questões no nível âncora → ajuste em Fase 2 e 3
PERCENTUAL_POR_NIVEL = {
    "basico": 25.0,        # nível 1-2
    "intermediario": 50.0, # nível 2-3
    "avancado": 70.0,      # nível 3-4
    "expert": 85.0,        # nível 4-5
}

# Sessões por peso do tópico
SESSOES_ALTO = [
    ("teoria_pdf", 50),
    ("exercicios", 45),
    ("video", 30),
    ("flashcard_texto", 20),
]
SESSOES_MEDIO = [
    ("teoria_pdf", 50),
    ("exercicios", 45),
    ("flashcard_texto", 20),
]
SESSOES_COMPLEMENTAR = [
    ("teoria_pdf", 50),
    ("exercicios", 45),
]

FATORES_NIVEL = {"conservador": 0.85, "moderado": 0.75, "agressivo": 0.65}


def _sessoes_para_peso(peso: float):
    if peso >= 0.7:
        return SESSOES_ALTO
    elif peso >= 0.3:
        return SESSOES_MEDIO
    else:
        return SESSOES_COMPLEMENTAR


def _estimar_nivel(tempo: str) -> str:
    return NIVEL_POR_TEMPO.get(tempo, "intermediario")


def _registrar_nivel_inicial_perfilb(
    tempo_por_materia: Dict[str, str], aluno_id: str, db: Session
) -> Dict[str, str]:
    """
    Persiste Proficiencia seed para cada matéria declarada no Perfil B.
    fonte='calibracao', percentual estimado pelo tempo declarado.
    Âncora usada na Fase 1 da calibração adaptativa (15q em 3 fases).
    """
    nivel_inicial: Dict[str, str] = {}
    for materia, tempo in tempo_por_materia.items():
        nivel = _estimar_nivel(tempo)
        percentual = PERCENTUAL_POR_NIVEL[nivel]
        nivel_inicial[materia] = nivel

        # Busca tópicos que correspondam à matéria (nível 0 = matéria raiz)
        topicos_mat = (
            db.query(Topico)
            .filter(Topico.ativo == True, Topico.nome.ilike(f"%{materia}%"))
            .all()
        )

        if topicos_mat:
            for topico in topicos_mat:
                prof = Proficiencia(
                    id=str(uuid.uuid4()),
                    aluno_id=aluno_id,
                    topico_id=topico.id,
                    materia=materia,
                    acertos=0,
                    total=0,
                    percentual=percentual,
                    fonte="calibracao",
                    peso_fonte=PESO_POR_FONTE["calibracao"],
                )
                db.add(prof)
        else:
            # Sem tópico cadastrado ainda — salva só com matéria
            prof = Proficiencia(
                id=str(uuid.uuid4()),
                aluno_id=aluno_id,
                topico_id=None,
                materia=materia,
                acertos=0,
                total=0,
                percentual=percentual,
                fonte="calibracao",
                peso_fonte=PESO_POR_FONTE["calibracao"],
            )
            db.add(prof)

    return nivel_inicial


def _importar_csv(dados_csv: list, aluno_id: str, db: Session) -> int:
    """Importa dados do CSV Qconcursos/TEC → Proficiencia."""
    count = 0
    for row in dados_csv:
        materia = row.get("materia") or row.get("disciplina") or ""
        acertos = int(row.get("acertos", 0))
        total = int(row.get("total", row.get("questoes", 0)))
        percentual = (acertos / total * 100) if total > 0 else 0.0
        fonte_raw = str(row.get("fonte", "qconcursos")).lower()
        fonte = "qconcursos" if "qconcursos" in fonte_raw else "tec"

        prof = Proficiencia(
            id=str(uuid.uuid4()),
            aluno_id=aluno_id,
            materia=materia,
            acertos=acertos,
            total=total,
            percentual=percentual,
            fonte=fonte,
            peso_fonte=PESO_POR_FONTE.get(fonte, 1.0),
        )
        db.add(prof)
        count += 1
    return count


def _gerar_sessoes(topicos: list, cronograma_id: str, aluno_id: str, db: Session) -> int:
    """Gera sessões multimodais para todos os tópicos do cronograma."""
    now = datetime.now(timezone.utc)
    count = 0
    for i, topico in enumerate(topicos):
        peso = topico.peso_edital or 1.0
        plano = _sessoes_para_peso(peso)
        for ordem, (tipo, duracao) in enumerate(plano):
            sessao = Sessao(
                id=str(uuid.uuid4()),
                aluno_id=aluno_id,
                topico_id=topico.id,
                cronograma_id=cronograma_id,
                tipo=tipo,
                duracao_planejada_min=duracao,
                uma_vez=(tipo == "calibracao"),
                data_agendada=now + timedelta(days=i),
            )
            db.add(sessao)
            count += 1
    return count


@router.post("", response_model=OnboardingResponse, status_code=201)
def onboarding(
    body: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    # ── 1. Resolver aluno ────────────────────────────────────────────────
    aluno = None

    if current_user:
        # Usuário já autenticado — atualiza perfil existente
        aluno = current_user
        aluno.area = body.area
        aluno.horas_por_dia = body.horas_por_dia
        aluno.dias_por_semana = body.dias_por_semana
        if body.data_prova:
            aluno.data_prova = datetime.combine(body.data_prova, datetime.min.time())
        db.flush()
    elif body.email and body.senha and body.nome:
        # Novo cadastro via onboarding
        if db.query(Aluno).filter(Aluno.email == body.email).first():
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")
        aluno = Aluno(
            nome=body.nome,
            email=body.email,
            senha_hash=hash_password(body.senha),
            area=body.area,
            data_prova=datetime.combine(body.data_prova, datetime.min.time()) if body.data_prova else None,
            horas_por_dia=body.horas_por_dia,
            dias_por_semana=body.dias_por_semana,
        )
        db.add(aluno)
        db.flush()
    else:
        raise HTTPException(
            status_code=400,
            detail="Forneça nome, email e senha para criar a conta no onboarding.",
        )

    # ── 2. Cronograma ─────────────────────────────────────────────────────
    cronograma = Cronograma(
        id=str(uuid.uuid4()),
        aluno_id=aluno.id,
    )
    db.add(cronograma)
    db.flush()

    # ── 3. Perfil B — nível inicial por matéria ───────────────────────────
    nivel_inicial: Dict[str, str] = {}
    if body.perfil == "tempo_por_materia" and body.tempo_por_materia:
        nivel_inicial = _registrar_nivel_inicial_perfilb(
            body.tempo_por_materia, aluno.id, db
        )

    # ── 3. Perfil C — importar CSV ────────────────────────────────────────
    if body.perfil == "csv" and body.dados_csv:
        _importar_csv(body.dados_csv, aluno.id, db)

    # ── 4. Gerar sessões com tópicos base (genéricos se sem edital) ───────
    topicos = db.query(Topico).filter(Topico.ativo == True).limit(50).all()
    sessoes_count = _gerar_sessoes(topicos, cronograma.id, aluno.id, db)

    # ── 5. Meta semanal inicial ───────────────────────────────────────────
    agora = datetime.now(timezone.utc)
    fator = FATORES_NIVEL.get(aluno.nivel_desafio, 0.75)
    carga_meta = int(body.horas_por_dia * body.dias_por_semana * 60 * fator)
    meta = MetaSemanal(
        id=str(uuid.uuid4()),
        aluno_id=aluno.id,
        janela_inicio=agora,
        janela_fim=agora + timedelta(days=7),
        nivel=aluno.nivel_desafio,
        carga_meta_min=carga_meta,
    )
    db.add(meta)

    db.commit()

    return OnboardingResponse(
        aluno_id=aluno.id,
        cronograma_id=cronograma.id,
        nivel_inicial=nivel_inicial,
        sessoes_geradas=sessoes_count,
        mensagem=(
            f"Cronograma gerado com {sessoes_count} sessões. "
            f"Meta semanal: {carga_meta} min."
        ),
    )
