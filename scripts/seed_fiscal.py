"""
scripts/seed_fiscal.py — Repopula a hierarquia fiscal no banco de dados.

Uso:
    railway run python scripts/seed_fiscal.py
    # ou localmente:
    python scripts/seed_fiscal.py

Ação:
  1. Remove todos os tópicos com area='fiscal' (e seus filhos, ciclos e subtopico_areas)
  2. Recria as 11 matérias fiscais (Área Fiscal — TEC Concursos) em 3 níveis:
       nivel=0  matéria raiz
       nivel=1  módulo / bloco de tópicos
       nivel=2  subtópico folha
  3. Cria CicloMateria para cada matéria (ordem por índice)
"""

import sys
import os

# Garante que o projeto raiz está no PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from app.core.database import SessionLocal
from app.models.topico import Topico
from app.models.ciclo_materia import CicloMateria

# ---------------------------------------------------------------------------
# Hierarquia completa — Área Fiscal (TEC Concursos)
# Formato: { "nome": str, "modulos": [ { "nome": str, "subtopicos": [str] } ] }
# ---------------------------------------------------------------------------
HIERARQUIA_FISCAL = [
    {
        "nome": "Direito Tributário",
        "modulos": [
            {
                "nome": "Módulo 1 — Teoria Geral e Espécies",
                "subtopicos": [
                    "Conceito de Tributo",
                    "Classificação Doutrinária dos Tributos",
                    "Natureza Jurídica Específica dos Tributos",
                    "Impostos (Conceito e Classificações)",
                    "Taxas (CF/1988 e CTN)",
                    "Contribuição de Melhoria (CF/1988 e CTN)",
                    "Empréstimo Compulsório (CF/1988 e CTN)",
                    "Contribuições Especiais (CF/1988)",
                    "Questões Mescladas de Espécies de Tributos",
                ],
            },
            {
                "nome": "Módulo 2 — Sistema Tributário Nacional (CF)",
                "subtopicos": [
                    "Princípios Tributários",
                    "Imunidades Tributárias",
                    "Competência para Legislar sobre Direito Tributário",
                    "Competência Tributária: Conceitos e Características",
                    "Repartição da Competência Tributária",
                    "Bitributação e Bis in Idem",
                    "Repartição Constitucional de Receitas (arts. 157 a 162 da CF)",
                ],
            },
            {
                "nome": "Módulo 3 — Normas Gerais (CTN)",
                "subtopicos": [
                    "Disposições Gerais da Legislação (arts. 96 a 100)",
                    "Vigência e Aplicação (arts. 101 a 106)",
                    "Interpretação e Integração (arts. 107 a 112)",
                    "Espécies Normativas Aplicadas ao Direito Tributário",
                    "Disposições Gerais da Obrigação Tributária",
                    "Fato Gerador (arts. 114 a 118)",
                    "Sujeito Ativo e Passivo (arts. 119 a 123)",
                    "Solidariedade (arts. 124 e 125)",
                    "Capacidade Tributária (art. 126)",
                    "Domicílio Tributário (art. 127)",
                    "Responsabilidade Tributária (arts. 128 a 138)",
                    "Disposições Gerais do Crédito Tributário",
                    "Lançamento e Constituição (arts. 142 a 150)",
                    "Suspensão da Exigibilidade (arts. 151 a 155-A)",
                    "Extinção do Crédito Tributário (arts. 156 a 174)",
                    "Exclusão do Crédito Tributário (arts. 175 a 182)",
                    "Garantias e Privilégios do Crédito (arts. 183 a 193)",
                    "Fiscalização Tributária (arts. 194 a 200)",
                    "Dívida Ativa Tributária (arts. 201 a 204)",
                    "Certidão Negativa (arts. 205 a 208)",
                    "Disposições Finais e Transitórias do CTN",
                ],
            },
            {
                "nome": "Módulo 4 — Impostos em Espécie e Reforma",
                "subtopicos": [
                    "II, IE, IR, IPI, IOF, ITR e IGF",
                    "ICMS, IPVA e ITCMD",
                    "ISS, IPTU e ITBI",
                    "IBS, CBS, Comitê Gestor e Imposto Seletivo (Reforma EC 132/2023)",
                ],
            },
            {
                "nome": "Módulo 5 — Processo e Temas Especiais",
                "subtopicos": [
                    "Processo Administrativo Tributário (PAT)",
                    "Processo Judicial Tributário",
                    "Lei de Execução Fiscal (Lei 6.830/80)",
                    "Medida Cautelar Fiscal, Mandado de Segurança e Tutelas",
                    "Elisão, Evasão e Elusão Fiscal",
                    "Direito Tributário Internacional",
                ],
            },
            {
                "nome": "Módulo 6 — Jurisprudência Tributária",
                "subtopicos": [
                    "Jurisprudência dos Tribunais Superiores (STF/STJ)",
                ],
            },
        ],
    },
    {
        "nome": "Direito Administrativo",
        "modulos": [
            {
                "nome": "Módulo 1 — Fundamentos e Atos Administrativos",
                "subtopicos": [
                    "Introdução (Origem, Conceito e Fontes)",
                    "Regime Jurídico Administrativo (Princípios Expressos e Implícitos)",
                    "Conceito e Mérito Administrativo",
                    "Elementos (COMFIFORMOB) e Atributos (PATI)",
                    "Classificação e Espécies de Atos",
                    "Extinção (Anulação, Revogação e Cassação)",
                    "Convalidação e Teoria dos Motivos Determinantes",
                ],
            },
            {
                "nome": "Módulo 2 — Poderes e Organização do Estado",
                "subtopicos": [
                    "Poderes Vinculado, Discricionário, Regulamentar, Hierárquico e Disciplinar",
                    "Poder de Polícia (Ciclo e Atributos)",
                    "Abuso de Poder (Excesso e Desvio de Finalidade)",
                    "Administração Direta e Indireta",
                    "Desconcentração e Descentralização",
                    "Lei 13.303/2016 (Estatuto das Estatais)",
                    "Terceiro Setor (OS, OSCIP, Sistema S, MROSC)",
                ],
            },
            {
                "nome": "Módulo 3 — Agentes Públicos e Lei 8.112/90",
                "subtopicos": [
                    "Conceito, Classificação e Acessibilidade",
                    "Acumulação de Cargos e Estabilidade (art. 37 a 41 da CF)",
                    "Remuneração e Teto Constitucional",
                    "Provimento e Vacância (Lei 8.112/90)",
                    "Direitos e Vantagens (Férias, Licenças, Adicionais)",
                    "Regime Disciplinar (Deveres, Proibições e Sanções)",
                    "Processo Administrativo Disciplinar (PAD) e Sindicância",
                ],
            },
            {
                "nome": "Módulo 4 — Gestão Pública, Responsabilidade e Controle",
                "subtopicos": [
                    "Conceito, Princípios e Classificação de Serviços Públicos",
                    "Concessões e Permissões (Lei 8.987/95)",
                    "Parcerias Público-Privadas (Lei 11.079/04) e Consórcios (Lei 11.107/05)",
                    "Teoria Objetiva e Risco Administrativo",
                    "Responsabilidade por Omissão",
                    "Excludentes e Direito de Regresso",
                    "Autotutela, Controle Judicial e Controle Legislativo",
                    "Desapropriação, Servidão, Requisição, Ocupação, Limitação e Tombamento",
                ],
            },
            {
                "nome": "Módulo 5 — Ética, Probidade e Processo",
                "subtopicos": [
                    "Atos de Improbidade (Enriquecimento, Prejuízo e Princípios)",
                    "Sanções, Prescrição e ANPC (Lei 8.429/1992)",
                    "Lei Anticorrupção e Acordo de Leniência (Lei 12.846/2013)",
                    "Processo Administrativo Federal (Lei 9.784/1999)",
                    "Lei de Acesso à Informação — Transparência e Sigilo (Lei 12.527/2011)",
                ],
            },
            {
                "nome": "Módulo 6 — Licitações e Contratos (Lei 14.133/2021)",
                "subtopicos": [
                    "Âmbito de Aplicação, Princípios e Fase Preparatória (ETP)",
                    "Modalidades (incluindo Diálogo Competitivo e Pregão)",
                    "Contratação Direta (Inexigibilidade e Dispensa)",
                    "Instrumentos Auxiliares (SRP)",
                    "Alocação de Riscos, Garantias e Duração dos Contratos",
                    "Alteração, Equilíbrio Econômico e Extinção",
                    "Sanções, Recursos e Portal Nacional de Contratações (PNCP)",
                    "Regulamentação Complementar (Decretos 2022-2024)",
                    "Legislação Esparsa (Informática, Publicidade e Estatais)",
                ],
            },
            {
                "nome": "Módulo 7 — Jurisprudência",
                "subtopicos": [
                    "Informativos e Súmulas (STF e STJ)",
                ],
            },
        ],
    },
    {
        "nome": "Direito Constitucional",
        "modulos": [
            {
                "nome": "Módulo 1 — Teoria e Princípios Fundamentais",
                "subtopicos": [
                    "Conceito, Estrutura e Classificação das Constituições",
                    "Aplicabilidade e Eficácia das Normas",
                    "Poder Constituinte (Originário, Derivado e Mutação)",
                    "Interpretação e Hermenêutica Constitucional",
                    "Aplicação no Tempo (Recepção e Repristinação)",
                    "Fundamentos, Objetivos e Princípios Internacionais (arts. 1º ao 4º)",
                ],
            },
            {
                "nome": "Módulo 2 — Direitos e Garantias Fundamentais",
                "subtopicos": [
                    "Direitos em Espécie e Características (art. 5º)",
                    "Remédios Constitucionais (HC, MS, MI, HD, AP)",
                    "Direitos Sociais e dos Trabalhadores (arts. 6º a 11)",
                    "Nacionalidade (Natos/Naturalizados e Perda)",
                    "Direitos Políticos (Soberania, Inelegibilidades e Perda/Suspensão)",
                    "Partidos Políticos (art. 17)",
                ],
            },
            {
                "nome": "Módulo 3 — Organização do Estado e Administração",
                "subtopicos": [
                    "Competências da União, Estados, DF e Municípios (arts. 18 a 36)",
                    "Intervenção Federal e Estadual",
                    "Disposições Gerais e Servidores Públicos (arts. 37 a 43)",
                ],
            },
            {
                "nome": "Módulo 4 — Organização dos Poderes",
                "subtopicos": [
                    "Congresso Nacional, Atribuições e Imunidades Parlamentares",
                    "Processo Legislativo (PEC, Leis, MPs e Vetos)",
                    "Fiscalização Contábil/Financeira — TCU",
                    "Atribuições e Responsabilidades do Presidente",
                    "Estatuto da Magistratura, Garantias e Vedações",
                    "Precatórios, STF, Súmulas Vinculantes, CNJ e STJ",
                    "Justiças Especializadas (Federal, Trabalho, Eleitoral e Militar)",
                    "Ministério Público, Advocacia Pública e Defensoria Pública",
                ],
            },
            {
                "nome": "Módulo 5 — Defesa do Estado e Tributação",
                "subtopicos": [
                    "Estado de Defesa, Estado de Sítio e Forças Armadas",
                    "Segurança Pública",
                    "Sistema Tributário Nacional (Limitações e Impostos)",
                    "Finanças Públicas: PPA, LDO e LOA",
                ],
            },
            {
                "nome": "Módulo 6 — Ordem Econômica, Social e ADCT",
                "subtopicos": [
                    "Princípios Econômicos, Atuação do Estado e Sistema Financeiro",
                    "Seguridade Social (Saúde, Previdência e Assistência)",
                    "Educação, Cultura, Meio Ambiente, Família e Índios",
                    "Disposições Finais e Transitórias (ADCT)",
                ],
            },
            {
                "nome": "Módulo 7 — Controle de Constitucionalidade e Jurisprudência",
                "subtopicos": [
                    "Modelos de Controle (Preventivo/Repressivo)",
                    "Controle Difuso (Incidental)",
                    "Controle Concentrado (ADI, ADC, ADO e ADPF)",
                    "Informativos e Temas de Repercussão Geral (STF e STJ)",
                ],
            },
        ],
    },
    {
        "nome": "Contabilidade Geral e Avançada",
        "modulos": [
            {
                "nome": "Módulo 1 — Fundamentos e Estrutura Inicial",
                "subtopicos": [
                    "Conceito, Objeto, Campo de Aplicação e Técnicas Contábeis",
                    "Teoria das Contas (Natureza Devedora e Credora)",
                    "CPC 00 (R2): Estrutura Conceitual",
                    "Atos e Fatos Contábeis (Permutativos, Modificativos e Mistos)",
                    "Lançamentos Contábeis (1ª, 2ª, 3ª e 4ª Fórmulas)",
                    "Livros Diário e Razão; Balancete de Verificação",
                    "Regimes de Competência vs. Caixa",
                ],
            },
            {
                "nome": "Módulo 2 — Ciclo Operacional e Ativos",
                "subtopicos": [
                    "Critérios de Avaliação de Estoques: PEPS e Média Ponderada (CPC 16)",
                    "Operações com Mercadorias (CMV, RCM e Tributos Recuperáveis)",
                    "Disponibilidades e Conciliação Bancária",
                    "Contas a Receber e PECLD",
                    "Ajuste a Valor Presente (AVP - CPC 12)",
                    "Investimentos: Avaliação pelo Custo ou MEP",
                    "Imobilizado: Mensuração e Depreciação",
                    "Intangível (CPC 04): Ágio (Goodwill)",
                    "CPC 01 (Impairment): Redução ao Valor Recuperável",
                ],
            },
            {
                "nome": "Módulo 3 — Passivo e Patrimônio Líquido",
                "subtopicos": [
                    "Empréstimos, Financiamentos e Debêntures (CPC 08)",
                    "CPC 25: Provisões, Passivos e Ativos Contingentes",
                    "Capital Social (Subscrito, a Realizar e Realizado)",
                    "Reservas de Lucros e Reservas de Capital",
                    "Ajuste de Avaliação Patrimonial (AAP)",
                ],
            },
            {
                "nome": "Módulo 4 — Demonstrações Contábeis",
                "subtopicos": [
                    "DRE: Estrutura e apuração do Lucro Líquido",
                    "DRA: Demonstração de Resultados Abrangentes",
                    "DFC (CPC 03): Métodos Direto e Indireto",
                    "DVA (CPC 09): Valor Adicionado",
                    "DMPL/DLPA: Mutações do PL",
                    "Notas Explicativas e Consolidação (CPC 36)",
                ],
            },
            {
                "nome": "Módulo 5 — Normas Especiais e Contabilidade Digital",
                "subtopicos": [
                    "CPC 06: Arrendamentos (Direito de Uso)",
                    "CPC 47: Receita de Contrato com Cliente",
                    "CPC 24: Eventos Subsequentes",
                    "ECD e Sistema SPED",
                    "Dividendos e Juros sobre Capital Próprio (JCP)",
                ],
            },
        ],
    },
    {
        "nome": "Língua Portuguesa",
        "modulos": [
            {
                "nome": "Módulo 1 — Bases da Escrita e Sons",
                "subtopicos": [
                    "Fonemas, Dígrafos e Encontros Vocálicos/Consonantais",
                    "Separação Silábica",
                    "Emprego das Letras (X/CH, S/Z, J/G)",
                    "Acentuação Gráfica (Regras e Novo Acordo)",
                    "Uso do Hífen",
                    "Iniciais Maiúsculas e Convenções de Escrita",
                ],
            },
            {
                "nome": "Módulo 2 — Morfologia",
                "subtopicos": [
                    "Estrutura e Formação de Palavras",
                    "Substantivo, Artigo, Adjetivo, Numeral, Interjeição e Advérbio",
                    "Conjugação, Reconhecimento e Emprego de Tempos/Modos Verbais",
                    "Correlação Verbal e Locuções Verbais",
                    "Pronomes Pessoais, Possessivos, Indefinidos e Interrogativos",
                    "Pronomes Demonstrativos",
                    "Pronomes Relativos",
                    "Conjunções Coordenativas e Subordinativas",
                    "Preposições",
                ],
            },
            {
                "nome": "Módulo 3 — Semântica e Coesão",
                "subtopicos": [
                    "Sinônimos/Antônimos e Homônimos/Parônimos",
                    "Denotação vs Conotação e Polissemia",
                    "Anáfora e Catáfora",
                    "Ordenação de Parágrafos e Significação de Vocábulos",
                ],
            },
            {
                "nome": "Módulo 4 — Sintaxe",
                "subtopicos": [
                    "Sujeito (Tipos) e Predicado",
                    "Objetos (Direto/Indireto), Agente da Passiva e Complemento Nominal",
                    "Adjuntos (Adnominal/Adverbial), Aposto e Vocativo",
                    "Adjunto Adnominal x Complemento Nominal",
                    "Orações Coordenadas e Subordinadas",
                    "Orações Reduzidas",
                    "Uso da Vírgula (Casos proibidos, obrigatórios e facultativos)",
                    "Travessão, Aspas, Dois-pontos e Parênteses",
                ],
            },
            {
                "nome": "Módulo 5 — Concordância, Regência e Crase",
                "subtopicos": [
                    "Concordância Verbal e Nominal",
                    "Regência Verbal e Nominal",
                    "Crase (Regras e Exceções)",
                    "Vozes Verbais (Ativa, Passiva e Reflexiva)",
                ],
            },
            {
                "nome": "Módulo 6 — Interpretação, Estilo e Partículas Especiais",
                "subtopicos": [
                    "Partícula 'Se' (Apassivadora, Indeterminadora)",
                    "Vocábulos 'Que' e 'Como'",
                    "Interpretação de Textos (Compreensão, Tipologia e Gêneros)",
                    "Reescrita de Frases",
                    "Paralelismo Sintático/Semântico",
                    "Figuras, Vícios e Funções da Linguagem",
                ],
            },
        ],
    },
    {
        "nome": "Auditoria",
        "modulos": [
            {
                "nome": "Módulo 1 — Fundamentos e Normas Profissionais",
                "subtopicos": [
                    "Trabalhos de Asseguração (Razoável vs. Limitada)",
                    "NBC TA 200: Objetivos Gerais do Auditor",
                    "Ceticismo e Julgamento Profissional",
                    "Princípios Éticos e Independência do Auditor",
                    "NBC TA 220 / NBC PA 01: Controle de Qualidade",
                ],
            },
            {
                "nome": "Módulo 2 — Planejamento e Identificação de Riscos",
                "subtopicos": [
                    "Estratégia Global vs. Plano de Auditoria (NBC TA 300)",
                    "Risco de Auditoria (Inerente, de Controle e de Detecção)",
                    "Identificação de Distorções Relevantes (NBC TA 315)",
                    "Materialidade no Planejamento e Execução (NBC TA 320)",
                    "Responsabilidade do Auditor e Fraude (NBC TA 240)",
                ],
            },
            {
                "nome": "Módulo 3 — Execução e Evidências",
                "subtopicos": [
                    "Adequação e Suficiência das Provas (NBC TA 500)",
                    "Procedimentos: Inspeção, Observação, Indagação, Recálculo",
                    "Procedimentos Analíticos",
                    "Amostragem Estatística vs. Não Estatística (NBC TA 530)",
                    "Auditoria de Estimativas Contábeis e Contingências",
                    "Papéis de Trabalho: Propriedade, Custódia e Sigilo (NBC TA 230)",
                ],
            },
            {
                "nome": "Módulo 4 — Conclusão e Relatórios",
                "subtopicos": [
                    "Tipos de Relatório: Sem Ressalva vs. Modificado",
                    "Opinião Modificada: Com Ressalva, Adversa e Abstenção",
                    "Parágrafos de Ênfase e Outros Assuntos",
                    "Eventos Subsequentes (NBC TA 560)",
                    "Continuidade Operacional (NBC TA 570)",
                    "Carta de Responsabilidade da Administração",
                ],
            },
            {
                "nome": "Módulo 5 — Auditoria Interna, Governança e Risco",
                "subtopicos": [
                    "Diferenças entre Auditoria Interna e Externa (NBC TI 01)",
                    "COSO ICIF (Controle Interno) e COSO ERM (Gestão de Riscos)",
                    "Lei Sarbanes-Oxley (SOX)",
                    "Princípios e Governança no Setor Público",
                ],
            },
            {
                "nome": "Módulo 6 — Especialidades e Normas Complementares",
                "subtopicos": [
                    "Perícia Contábil (NBC TP 01 e PP 01)",
                    "Normas do BACEN e da CVM",
                ],
            },
        ],
    },
    {
        "nome": "Direito Civil",
        "modulos": [
            {
                "nome": "Módulo 1 — Lei de Introdução e Parte Geral",
                "subtopicos": [
                    "Pessoas Naturais: Personalidade, Capacidade e Direitos da Personalidade",
                    "Pessoas Jurídicas: Disposições Gerais, Associações e Fundações",
                    "Desconsideração da Personalidade Jurídica",
                    "Domicílio das Pessoas Naturais e Jurídicas",
                    "Classificação dos Bens e Bens Públicos",
                ],
            },
            {
                "nome": "Módulo 2 — Fatos Jurídicos e Negócio Jurídico",
                "subtopicos": [
                    "Teoria Geral dos Fatos Jurídicos",
                    "Classificações e Disposições Gerais do Negócio Jurídico",
                    "Representação (arts. 115 a 120)",
                    "Condição, Termo e Encargo",
                    "Defeitos ou Vícios do Negócio Jurídico",
                    "Invalidade do Negócio Jurídico",
                    "Atos Ilícitos",
                    "Prescrição e Decadência",
                    "Prova do Negócio Jurídico",
                ],
            },
            {
                "nome": "Módulo 3 — Direito das Obrigações",
                "subtopicos": [
                    "Obrigações de Dar, Fazer e Não Fazer",
                    "Obrigações Alternativas, Divisíveis e Solidárias",
                    "Cessão de Crédito e Assunção de Dívida",
                    "Pagamento e Formas de Extinção da Obrigação",
                    "Mora, Perdas e Danos, Juros Legais e Cláusula Penal",
                ],
            },
            {
                "nome": "Módulo 4 — Contratos",
                "subtopicos": [
                    "Princípios e Classificação dos Contratos",
                    "Formação, Vícios Redibitórios e Evicção",
                    "Extinção dos Contratos",
                    "Compra e Venda, Doação, Locação, Mandato",
                    "Seguro, Fiança, Transação e demais espécies",
                ],
            },
            {
                "nome": "Módulo 5 — Atos Unilaterais e Responsabilidade Civil",
                "subtopicos": [
                    "Promessa de Recompensa, Gestão de Negócios",
                    "Pagamento Indevido e Enriquecimento Sem Causa",
                    "Responsabilidade Civil: Disposições Gerais",
                ],
            },
            {
                "nome": "Módulo 6 — Direito das Coisas",
                "subtopicos": [
                    "Posse: Teorias, Aquisição, Efeitos e Perda",
                    "Propriedade: Aquisição, Perda e Direito de Vizinhança",
                    "Condomínio e Propriedades Especiais",
                    "Superfície, Servidões, Usufruto, Uso e Habitação",
                    "Penhor, Hipoteca e Anticrese",
                ],
            },
            {
                "nome": "Módulo 7 — Direito de Família e Sucessões",
                "subtopicos": [
                    "Casamento, Regime de Bens e União Estável",
                    "Alimentos, Guarda e Parentesco",
                    "Tutela, Curatela e Tomada de Decisão Apoiada",
                    "Herança, Vocação Hereditária e Testamentos",
                    "Inventário e Partilha",
                ],
            },
            {
                "nome": "Módulo 8 — Disposições Finais e Transitórias",
                "subtopicos": [
                    "Regras de Transição e Enfiteuse",
                ],
            },
        ],
    },
    {
        "nome": "Direito Empresarial",
        "modulos": [
            {
                "nome": "Módulo 1 — Teoria Geral do Empresário",
                "subtopicos": [
                    "Conceito, Autonomia, Fontes e Princípios",
                    "Caracterização e Inscrição do Empresário Individual",
                    "Capacidade Empresarial",
                ],
            },
            {
                "nome": "Módulo 2 — Estabelecimento, Registro e Escrituração",
                "subtopicos": [
                    "Do Estabelecimento (arts. 1.142 a 1.149 do CC)",
                    "Do Registro (arts. 1.150 a 1.154 do CC)",
                    "Nome Empresarial, Prepostos e Escrituração",
                ],
            },
            {
                "nome": "Módulo 3 — Direito Societário",
                "subtopicos": [
                    "Sociedade em Comum e em Conta de Participação",
                    "Sociedade Simples e em Nome Coletivo",
                    "Sociedade em Comandita Simples",
                    "Sociedade Limitada (arts. 1.052 a 1.087)",
                    "Sociedade Cooperativa",
                    "Dissolução, Liquidação e Extinção das Sociedades",
                    "Operações Societárias (Fusão, Cisão, Incorporação)",
                ],
            },
            {
                "nome": "Módulo 4 — Sociedade Anônima (Lei 6.404/1976)",
                "subtopicos": [
                    "Características e Constituição da Companhia",
                    "Capital Social, Ações, Debêntures e Bônus",
                    "Governança: Assembleia, Conselhos e Diretoria",
                    "Dissolução, Liquidação e Extinção das SA",
                    "Grupos de Sociedades e Consórcio",
                ],
            },
            {
                "nome": "Módulo 5 — Títulos de Crédito",
                "subtopicos": [
                    "Conceito, Características e Princípios",
                    "Letra de Câmbio e Nota Promissória",
                    "Cheque (Lei 7.357/1985)",
                    "Duplicata (Lei 5.474/1968)",
                    "Protesto e demais espécies",
                ],
            },
            {
                "nome": "Módulo 6 — Falência e Recuperação de Empresas (Lei 11.101/2005)",
                "subtopicos": [
                    "Disposições Comuns à Recuperação e à Falência",
                    "Recuperação Judicial e Convolação em Falência",
                    "Da Falência (arts. 75 a 160)",
                    "Recuperação Extrajudicial",
                ],
            },
            {
                "nome": "Módulo 7 — Propriedade Industrial (Lei 9.279/1996)",
                "subtopicos": [
                    "Patentes, Desenhos Industriais e Marcas",
                    "Indicações Geográficas e Transferência de Tecnologia",
                    "Propriedade Intelectual de Software (Lei 9.609/1998)",
                ],
            },
            {
                "nome": "Módulo 8 — Contratos Mercantis",
                "subtopicos": [
                    "Contratos Bancários (Depósito, Mútuo, Desconto)",
                    "Alienação Fiduciária, Leasing e Factoring",
                    "Representação, Agência, Franquia (Lei 13.966/2019)",
                ],
            },
            {
                "nome": "Módulo 9 — Cooperativismo",
                "subtopicos": [
                    "História, Conceitos e Princípios",
                    "Lei 5.764/1971",
                ],
            },
            {
                "nome": "Módulo 10 — Jurisprudência",
                "subtopicos": [
                    "STJ e STF sobre Sociedades, Títulos e Falência",
                ],
            },
        ],
    },
    {
        "nome": "Matemática Financeira",
        "modulos": [
            {
                "nome": "Módulo 1 — Conceitos Fundamentais e Juros",
                "subtopicos": [
                    "Capital, Montante, Taxa e Desconto",
                    "Juros Simples e Taxas Proporcionais",
                    "Juros Compostos e Taxas Equivalentes",
                    "Taxas Efetivas, Nominais e Capitalização Contínua",
                    "Inflação, Juros Reais e Juros Aparentes",
                ],
            },
            {
                "nome": "Módulo 2 — Descontos",
                "subtopicos": [
                    "Desconto Comercial Simples e Racional Simples",
                    "Desconto Comercial Composto e Racional Composto",
                    "Relação entre Desconto Comercial e Racional",
                ],
            },
            {
                "nome": "Módulo 3 — Séries de Pagamentos e Fluxo de Caixa",
                "subtopicos": [
                    "Classificação das Rendas",
                    "Valor Atual de Uma Série de Pagamentos",
                    "Valor Futuro de Uma Série de Pagamentos",
                    "Equivalência de Capitais e Rearranjo do Fluxo",
                ],
            },
            {
                "nome": "Módulo 4 — Sistemas de Amortização",
                "subtopicos": [
                    "Sistema de Amortização Constante (SAC)",
                    "Sistema de Amortização Francês (Tabela Price)",
                    "Sistema de Amortização Americano e Alemão",
                    "Sistemas Mistos de Amortização",
                ],
            },
            {
                "nome": "Módulo 5 — Análise de Investimentos",
                "subtopicos": [
                    "Valor Presente Líquido (VPL)",
                    "Taxa Interna de Retorno (TIR) e TMA",
                    "Payback e Payback Descontado",
                    "Índice de Lucratividade e Taxa de Rentabilidade",
                    "Títulos com Cupons Periódicos (Bonds)",
                ],
            },
        ],
    },
    {
        "nome": "Raciocínio Lógico",
        "modulos": [
            {
                "nome": "Módulo 1 — Lógica Proposicional",
                "subtopicos": [
                    "Proposições e Operadores Lógicos",
                    "Ordem de Precedência entre Conectivos",
                    "Tabela Verdade das Proposições Compostas",
                    "Tautologia, Contradição e Contingência",
                    "Equivalências Lógicas e Negação de Proposições",
                    "Condição Necessária e Suficiente",
                ],
            },
            {
                "nome": "Módulo 2 — Lógica de Argumentação",
                "subtopicos": [
                    "Argumentos e Métodos da Tabela Verdade",
                    "Raciocínio Crítico",
                    "Argumentos Indutivos e por Abdução",
                    "Falácias",
                ],
            },
            {
                "nome": "Módulo 3 — Lógica de Primeira Ordem",
                "subtopicos": [
                    "Lógica de Primeira Ordem e Predicados",
                    "Diagramas Lógicos e Proposições Categóricas",
                    "Negação de Quantificadores",
                ],
            },
            {
                "nome": "Módulo 4 — Problemas de Lógica",
                "subtopicos": [
                    "Sequências de Números, Figuras e Letras",
                    "Associação de Informações",
                    "Exercícios de Verdade/Mentira",
                    "Parentesco, Datas e Calendários",
                    "Problemas com Balança, Palitos e Similares",
                ],
            },
            {
                "nome": "Módulo 5 — Lógica Espacial",
                "subtopicos": [
                    "Planificação de Sólidos e Projeções 3D",
                    "Orientação no Plano, no Espaço e no Tempo",
                ],
            },
        ],
    },
    {
        "nome": "Tecnologia da Informação",
        "modulos": [
            {
                "nome": "Módulo 1 — Organização e Arquitetura de Computadores",
                "subtopicos": [
                    "Sistemas de Numeração e Operações Lógicas",
                    "Arquitetura Von Neumann e Harvard, RISC vs CISC",
                    "Hierarquia de Memória (RAM, ROM, Cache)",
                    "HD, SSD, RAID e Periféricos",
                ],
            },
            {
                "nome": "Módulo 2 — Sistemas Operacionais",
                "subtopicos": [
                    "Gerência de Processos, Threads e Deadlock",
                    "Paginação, Memória Virtual e Sistemas de Arquivos",
                    "Windows (XP ao 11) e Comandos CMD/PowerShell",
                    "Linux: Kernel, Comandos de Terminal e Shell Script",
                    "Virtualização, Docker e Kubernetes",
                ],
            },
            {
                "nome": "Módulo 3 — Redes de Computadores e Internet",
                "subtopicos": [
                    "Modelo OSI (7 camadas) e TCP/IP (4 camadas)",
                    "IP (IPv4, IPv6), Sub-redes, ARP, DHCP e DNS",
                    "TCP, UDP e Protocolos de Roteamento",
                    "Ethernet, Wi-Fi 6, Bluetooth e VLANs",
                    "HTTP/HTTPS, FTP, SSH, VoIP e SNMP",
                ],
            },
            {
                "nome": "Módulo 4 — Segurança da Informação",
                "subtopicos": [
                    "ISO 27001/27002/27005, LGPD e Compliance",
                    "Criptografia Simétrica, Assimétrica e Hashes",
                    "Assinatura Digital e Certificados Digitais (ICP-Brasil)",
                    "Firewall, IDS/IPS, VPN e Zero Trust",
                    "Malware, Phishing, DoS/DDoS e OWASP Top 10",
                    "Backup (RPO/RTO), MFA e Controle de Acesso (RBAC)",
                ],
            },
            {
                "nome": "Módulo 5 — Engenharia de Software",
                "subtopicos": [
                    "RUP, Cascata, Espiral, Incremental e Prototipação",
                    "Scrum, Kanban, XP e SAFe",
                    "UML (Casos de Uso, Classes, Sequência)",
                    "Qualidade: ISO 12207, TDD, BDD e Tipos de Testes",
                    "Git, CI/CD e IaC",
                ],
            },
            {
                "nome": "Módulo 6 — Desenvolvimento de Sistemas",
                "subtopicos": [
                    "Microsserviços, SOA e Arquitetura Hexagonal",
                    "REST/RESTful, SOAP e gRPC",
                    "Estruturas de Dados e Princípios SOLID",
                    "Linguagens: Java, Python, .NET, C#",
                ],
            },
            {
                "nome": "Módulo 7 — Banco de Dados",
                "subtopicos": [
                    "MER, Mapeamento Relacional e Normalização",
                    "SQL: DDL, DML, DQL, Triggers e Views",
                    "Transações ACID e Controle de Concorrência",
                    "NoSQL: Modelos, Teorema CAP e MongoDB",
                ],
            },
            {
                "nome": "Módulo 8 — Ciência de Dados e IA",
                "subtopicos": [
                    "Data Warehouse, ETL e Modelagem Dimensional",
                    "OLAP (Drill-down, Roll-up, Slice, Dice)",
                    "Big Data: Hadoop, Data Lake e Apache Spark",
                    "Machine Learning: Supervisionado e Não Supervisionado",
                    "Power BI, Tableau e Python (Pandas, Scikit-Learn)",
                ],
            },
            {
                "nome": "Módulo 9 — Gestão e Governança de TI",
                "subtopicos": [
                    "COBIT (4.1, 5, 2019) e ITIL (v3 e v4)",
                    "BPM, BPMN e Processos de Negócio",
                    "IN SGD/ME 94/2022 e Guia de PDTIC",
                ],
            },
            {
                "nome": "Módulo 10 — Aplicativos e Ferramentas",
                "subtopicos": [
                    "Microsoft Office (Word, Excel, PowerPoint)",
                    "LibreOffice e Navegadores",
                    "Google Workspace e Microsoft Teams",
                ],
            },
        ],
    },
]


def seed():
    db = SessionLocal()
    try:
        print("=== Seed Fiscal — iniciando ===")

        # 1. Coletar IDs de todos os tópicos fiscais existentes (nível 0)
        materias_existentes = db.query(Topico).filter(
            Topico.nivel == 0, Topico.area == "fiscal"
        ).all()
        ids_materias = [t.id for t in materias_existentes]

        if ids_materias:
            # Coletar IDs dos módulos (nível 1) filhos dessas matérias
            modulos_existentes = db.query(Topico).filter(
                Topico.nivel == 1, Topico.parent_id.in_(ids_materias)
            ).all()
            ids_modulos = [t.id for t in modulos_existentes]

            # Coletar IDs dos subtópicos (nível 2)
            if ids_modulos:
                ids_subtopicos = [
                    t.id for t in db.query(Topico).filter(
                        Topico.nivel == 2, Topico.parent_id.in_(ids_modulos)
                    ).all()
                ]
                # Deletar subtópicos primeiro
                if ids_subtopicos:
                    db.query(Topico).filter(Topico.id.in_(ids_subtopicos)).delete(synchronize_session=False)

                # Deletar módulos
                db.query(Topico).filter(Topico.id.in_(ids_modulos)).delete(synchronize_session=False)

            # Deletar CicloMateria referenciando essas matérias
            db.query(CicloMateria).filter(
                CicloMateria.subject_id.in_(ids_materias)
            ).delete(synchronize_session=False)

            # Deletar matérias
            db.query(Topico).filter(Topico.id.in_(ids_materias)).delete(synchronize_session=False)

            db.commit()
            print(f"  Removidos: {len(ids_materias)} matérias, {len(ids_modulos)} módulos")

        # 2. Recriar a hierarquia
        total_mat = 0
        total_mod = 0
        total_sub = 0

        for ordem, mat_data in enumerate(HIERARQUIA_FISCAL):
            mat_id = str(uuid.uuid4())
            materia = Topico(
                id=mat_id,
                nome=mat_data["nome"],
                nivel=0,
                area="fiscal",
                ativo=True,
            )
            db.add(materia)

            # CicloMateria
            ciclo = CicloMateria(
                id=str(uuid.uuid4()),
                area="fiscal",
                subject_id=mat_id,
                ordem=ordem,
                ativo=True,
            )
            db.add(ciclo)
            total_mat += 1

            for modulo_data in mat_data["modulos"]:
                mod_id = str(uuid.uuid4())
                modulo = Topico(
                    id=mod_id,
                    nome=modulo_data["nome"],
                    nivel=1,
                    parent_id=mat_id,
                    area="fiscal",
                    ativo=True,
                )
                db.add(modulo)
                total_mod += 1

                for sub_nome in modulo_data["subtopicos"]:
                    sub = Topico(
                        id=str(uuid.uuid4()),
                        nome=sub_nome,
                        nivel=2,
                        parent_id=mod_id,
                        area="fiscal",
                        ativo=True,
                    )
                    db.add(sub)
                    total_sub += 1

        db.commit()
        print(f"  Criados: {total_mat} matérias, {total_mod} módulos, {total_sub} subtópicos")
        print("=== Seed Fiscal — concluído ===")

    except Exception as e:
        db.rollback()
        print(f"ERRO: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
