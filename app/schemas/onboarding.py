from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel


class OnboardingRequest(BaseModel):
    # Tela 1
    area: str = "fiscal"        # Fiscal / Jurídica / Policial / TI / Saúde / Outro

    # Tela 2
    tem_edital: bool = False
    data_prova: Optional[date] = None

    # Tela 3 — perfil
    perfil: str = "zero"        # zero | tempo_por_materia | csv
    # Perfil B: tempo declarado por matéria (ex: {"Direito Constitucional": "1-3m"})
    tempo_por_materia: Optional[Dict[str, str]] = None
    # Perfil C: dados do CSV Qconcursos/TEC (lista de dicts)
    dados_csv: Optional[List[Dict]] = None

    # Tela 4
    horas_por_dia: float = 3.0
    dias_por_semana: int = 5

    # Autenticação (opcional — se já logado, usa o token)
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None


class OnboardingResponse(BaseModel):
    aluno_id: str
    cronograma_id: str
    nivel_inicial: Dict[str, str]   # materia → nivel estimado
    sessoes_geradas: int
    mensagem: str
