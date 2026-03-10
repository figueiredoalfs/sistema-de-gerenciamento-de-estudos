"""
Script de seed: popula as tabelas Topico com as matérias e subtópicos padrão.

Uso:
    python -m app.scripts.seed_topicos

Cria:
  - 1 Topico nivel=0 por matéria (raiz)
  - N Topico nivel=2 por subtópico (folha)
  - decay_rate correto por categoria

Idempotente: pula tópicos já existentes (mesmo nome + nivel).
"""

import sys
import uuid

from app.core.database import SessionLocal
from app.models.topico import Topico
from app.services.decay import get_decay_rate

# Matérias e subtópicos padrão
MATERIAS_PADRAO: dict[str, list[str]] = {
    "Português": [
        "Interpretação de Texto", "Concordância Verbal e Nominal", "Regência Verbal e Nominal",
        "Colocação Pronominal", "Pontuação", "Ortografia e Acentuação", "Semântica e Sinônimos",
        "Crase", "Figuras de Linguagem", "Redação Oficial",
    ],
    "Raciocínio Lógico": [
        "Proposições e Conectivos Lógicos", "Equivalências Lógicas", "Silogismo",
        "Diagramas Lógicos", "Sequências e Progressões", "Análise Combinatória",
        "Probabilidade", "Problemas de Contagem", "Conjuntos e Operações", "Lógica de Argumentação",
    ],
    "Matemática": [
        "Aritmética Básica", "Porcentagem", "Razão e Proporção", "Regra de Três",
        "Operações com Frações", "Geometria Plana", "Álgebra e Equações",
        "Progressões (PA e PG)", "Estatística Básica", "Conjuntos",
    ],
    "Matemática Financeira": [
        "Juros Simples", "Juros Compostos", "Descontos", "Séries de Pagamentos",
        "Amortização", "Equivalência de Capitais", "VPL e TIR", "Fluxo de Caixa",
    ],
    "Direito Constitucional": [
        "Princípios Fundamentais", "Direitos e Garantias Fundamentais", "Remédios Constitucionais",
        "Organização do Estado", "Poder Legislativo", "Poder Executivo", "Poder Judiciário",
        "Controle de Constitucionalidade", "Processo Legislativo", "Ordem Econômica e Social",
    ],
    "Direito Administrativo": [
        "Princípios da Administração Pública", "Atos Administrativos", "Licitações (Lei 14.133/2021)",
        "Contratos Administrativos", "Servidores Públicos (Lei 8.112/1990)",
        "Responsabilidade Civil do Estado", "Processo Administrativo", "Poderes Administrativos",
        "Bens Públicos", "Controle da Administração", "Improbidade Administrativa",
    ],
    "Direito Penal": [
        "Parte Geral — Tipicidade e Culpabilidade", "Teoria da Pena", "Excludentes de Ilicitude",
        "Crimes contra a Pessoa", "Crimes contra o Patrimônio", "Crimes contra a Fé Pública",
        "Crimes contra a Administração Pública", "Lei de Drogas",
        "Circunstâncias Agravantes e Atenuantes", "Extinção da Punibilidade",
    ],
    "Direito Processual Penal": [
        "Inquérito Policial", "Ação Penal", "Prisão em Flagrante", "Prisão Preventiva e Temporária",
        "Medidas Cautelares", "Prova Penal", "Competência Jurisdicional", "Habeas Corpus",
        "Recursos", "Júri",
    ],
    "Direito Civil": [
        "Parte Geral", "Obrigações", "Contratos em Espécie", "Responsabilidade Civil",
        "Direito de Família", "Direito das Coisas", "Sucessões", "Posse e Propriedade",
    ],
    "Direito Processual Civil": [
        "Princípios", "Competência", "Processo de Conhecimento", "Tutelas Provisórias",
        "Provas", "Sentença e Coisa Julgada", "Recursos", "Execução", "Procedimentos Especiais",
    ],
    "Direito Tributário": [
        "Sistema Tributário Nacional", "Princípios Constitucionais Tributários",
        "Espécies de Tributos", "Obrigação Tributária", "Crédito Tributário",
        "Lançamento Tributário", "Extinção da Obrigação Tributária",
        "Exclusão do Crédito Tributário", "Responsabilidade Tributária",
        "Processo Tributário", "CTN (Lei 5.172/1966)",
    ],
    "Contabilidade": [
        "Balanço Patrimonial", "Demonstração de Resultado (DRE)", "Escrituração",
        "Patrimônio Líquido", "Depreciação e Amortização", "Análise das Demonstrações",
        "Contabilidade de Custos", "Contabilidade Pública", "Auditoria",
        "Normas Brasileiras de Contabilidade",
    ],
    "Administração": [
        "Teorias Administrativas", "Planejamento, Organização, Direção e Controle",
        "Gestão de Pessoas", "Gestão por Competências", "Liderança e Motivação",
        "Cultura Organizacional", "Gestão Estratégica", "Gestão de Projetos",
        "Qualidade e Produtividade", "Gestão por Processos",
    ],
    "Informática": [
        "Word (Microsoft / LibreOffice)", "Excel — Fórmulas e Funções", "PowerPoint",
        "Internet e Navegadores", "E-mail e Comunicação Digital",
        "Sistemas Operacionais (Windows / Linux)", "Hardware Básico",
        "Nuvem (OneDrive, Google Drive)", "Segurança Digital e Antivírus", "Backup e Recuperação",
    ],
    "Segurança da Informação": [
        "Criptografia", "Vírus, Malware e Ransomware", "Firewall e IDS/IPS",
        "Autenticação e Controle de Acesso", "Phishing e Engenharia Social",
        "Certificados Digitais", "LGPD (Lei 13.709/2018)",
        "Protocolos de Segurança (HTTPS, SSL/TLS)", "ISO 27001", "Gestão de Riscos",
    ],
    "Redes de Computadores": [
        "Modelos OSI e TCP/IP", "Endereçamento IP (IPv4 e IPv6)", "Subredes e Máscara de Rede",
        "Protocolos (HTTP, FTP, SMTP, DNS)", "Roteamento", "Switches e VLANs",
        "Topologias de Rede", "Wi-Fi e Cabeamento", "VPN", "Monitoramento de Rede",
    ],
    "Banco de Dados": [
        "Modelo Relacional", "SQL — SELECT e Filtros", "SQL — JOIN, GROUP BY, HAVING",
        "SQL — INSERT, UPDATE, DELETE", "Normalização (1FN, 2FN, 3FN)",
        "Índices e Otimização", "Transações e ACID", "Triggers e Procedures",
        "NoSQL (MongoDB, Redis)", "Backup e Recuperação",
    ],
    "Governança de TI": [
        "ITIL — Conceitos e Processos", "COBIT", "Gerenciamento de Incidentes",
        "Gerenciamento de Mudanças", "SLA e Gestão de Nível de Serviço",
        "Continuidade de Negócios", "Disaster Recovery", "ISO 20000",
        "Gestão de Capacidade", "Gestão de Configuração",
    ],
    "Legislação do SUS": [
        "Lei 8.080/1990 — Lei Orgânica da Saúde", "Lei 8.142/1990 — Participação Social",
        "Decreto 7.508/2011", "Princípios do SUS (Universalidade, Equidade, Integralidade)",
        "Diretrizes do SUS", "Organização e Gestão do SUS", "Financiamento do SUS",
        "Conselhos e Conferências de Saúde", "NOB e NOAS", "Pacto pela Saúde",
    ],
    "Saúde Pública": [
        "Epidemiologia Básica", "Indicadores de Saúde", "Vigilância em Saúde",
        "Doenças de Notificação Obrigatória", "Promoção da Saúde", "Prevenção de Doenças",
        "Determinantes Sociais da Saúde", "Surtos e Epidemias",
        "Saúde da Família (ESF)", "Atenção Primária à Saúde",
    ],
    "Atualidades": [
        "Política Nacional", "Política Internacional", "Economia Brasileira",
        "Meio Ambiente e Clima", "Ciência e Tecnologia", "Direitos Humanos",
        "Saúde e Pandemia", "Segurança Pública", "Educação", "Questões Sociais",
    ],
    "Legislação Específica": [
        "Lei Orgânica do Órgão", "Regimento Interno", "Estatuto do Servidor",
        "Código de Ética", "Legislação Ambiental", "Leis Complementares",
    ],
}


def seed(db=None) -> dict:
    close = db is None
    if db is None:
        db = SessionLocal()

    try:
        # Carrega nomes já existentes para evitar duplicatas
        existentes = {
            (t.nome, t.nivel)
            for t in db.query(Topico.nome, Topico.nivel).all()
        }

        materias_criadas = 0
        topicos_criados = 0

        for materia, subtopicos in MATERIAS_PADRAO.items():
            decay = get_decay_rate(materia)

            # Tópico raiz (nivel=0 = matéria)
            if (materia, 0) not in existentes:
                db.add(Topico(
                    id=str(uuid.uuid4()),
                    nome=materia,
                    nivel=0,
                    area=materia,
                    decay_rate=decay,
                    peso_edital=1.0,
                ))
                existentes.add((materia, 0))
                materias_criadas += 1

            # Subtópicos (nivel=2 = tópico folha)
            for sub in subtopicos:
                if (sub, 2) not in existentes:
                    db.add(Topico(
                        id=str(uuid.uuid4()),
                        nome=sub,
                        nivel=2,
                        area=materia,
                        decay_rate=decay,
                        peso_edital=1.0,
                    ))
                    existentes.add((sub, 2))
                    topicos_criados += 1

        db.commit()
        resultado = {"materias": materias_criadas, "topicos": topicos_criados}
        print(f"[OK] Seed concluido: {materias_criadas} materias + {topicos_criados} topicos criados.")
        return resultado

    except Exception as e:
        db.rollback()
        print(f"[ERRO] Seed falhou: {e}")
        raise
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    seed()
