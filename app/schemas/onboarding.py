from typing import List, Literal, Optional

from pydantic import BaseModel, model_validator

FUNCIONALIDADES_VALIDAS = {
    "geracao_conteudo",
    "analise_desempenho",
    "cronograma_estudo",
    "geracao_questoes",
}

TEMPOS_VALIDOS = {"<1m", "1-3m", "3-6m", ">6m"}


class OnboardingRequest(BaseModel):
    # Cadastro (obrigatório quando não autenticado)
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None

    # Passo 1 — área do concurso (apenas "fiscal" por enquanto)
    area: str = "fiscal"

    # Passo 2 — fase de estudo
    fase_estudo: Literal["pre_edital", "pos_edital"]

    # Passo 3 — experiência
    experiencia: Literal["iniciante", "tempo_de_estudo"]
    # Obrigatório quando experiencia == "tempo_de_estudo"; valores: "<1m", "1-3m", "3-6m", ">6m"
    tempo_estudo: Optional[str] = None

    # Passo 4 — funcionalidades desejadas (pelo menos 1)
    funcionalidades: List[str]

    @model_validator(mode="after")
    def validar_campos(self) -> "OnboardingRequest":
        if self.experiencia == "tempo_de_estudo":
            if not self.tempo_estudo:
                raise ValueError(
                    "tempo_estudo é obrigatório quando experiencia='tempo_de_estudo'"
                )
            if self.tempo_estudo not in TEMPOS_VALIDOS:
                raise ValueError(
                    f"tempo_estudo deve ser um de {sorted(TEMPOS_VALIDOS)}"
                )

        invalidas = set(self.funcionalidades) - FUNCIONALIDADES_VALIDAS
        if invalidas:
            raise ValueError(
                f"Funcionalidades inválidas: {invalidas}. "
                f"Válidas: {sorted(FUNCIONALIDADES_VALIDAS)}"
            )
        if not self.funcionalidades:
            raise ValueError("Selecione ao menos uma funcionalidade.")

        return self


class OnboardingResponse(BaseModel):
    aluno_id: str
    perfil_estudo_id: str
    funcionalidades: List[str]
    mensagem: str
