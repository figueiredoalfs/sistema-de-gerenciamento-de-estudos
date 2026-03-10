"""
config_materias.py
─────────────────────────────────────────────────────────────────────────────
Hierarquia de 3 níveis para matérias de concursos públicos:
  Matéria → Tópico → [Subtópico, ...]

Também define MATERIAS_POR_AREA: mapeamento de área → lista de matérias.

Uso:
  from config_materias import get_topicos, get_subtopicos, MATERIAS_POR_AREA
─────────────────────────────────────────────────────────────────────────────
"""

# ── Hierarquia completa ────────────────────────────────────────────────────────

HIERARQUIA: dict = {

    # ══════════════════════════════════════════════════════════════════════════
    # CONHECIMENTOS GERAIS E TRANSVERSAIS
    # ══════════════════════════════════════════════════════════════════════════

    "Língua Portuguesa": {
        "Compreensão e Interpretação Textual": [
            "Tipos e gêneros textuais",
            "Informações implícitas e explícitas",
            "Sentido figurado e conotativo",
            "Intelecção e inferência",
        ],
        "Ortografia e Acentuação": [
            "Novo Acordo Ortográfico",
            "Uso do hífen",
            "Acentuação gráfica",
            "Emprego de maiúsculas e minúsculas",
        ],
        "Morfologia": [
            "Classes de palavras (substantivo, adjetivo, verbo...)",
            "Formação de palavras (derivação, composição)",
            "Flexão nominal e verbal",
            "Pronomes: tipos e colocação pronominal",
        ],
        "Sintaxe": [
            "Termos essenciais e acessórios da oração",
            "Período composto por coordenação",
            "Período composto por subordinação",
            "Concordância nominal",
            "Concordância verbal",
            "Regência nominal e verbal",
            "Crase",
        ],
        "Semântica e Estilística": [
            "Sinonímia, antonímia e polissemia",
            "Figuras de linguagem",
            "Funções da linguagem",
            "Denotação e conotação",
        ],
        "Coesão e Coerência Textual": [
            "Conectivos e operadores argumentativos",
            "Referência e substituição",
            "Progressão temática",
            "Paralelismo",
        ],
        "Pontuação": [
            "Uso da vírgula",
            "Ponto-e-vírgula e dois-pontos",
            "Travessão, parênteses e aspas",
        ],
    },

    "Redação Oficial": {
        "Características e Princípios": [
            "Impessoalidade, clareza e concisão",
            "Formalidade e padronização",
            "Uso da norma culta",
        ],
        "Correspondências Oficiais": [
            "Ofício (padrão único)",
            "Memorando interno",
            "Email institucional",
            "Exposição de motivos",
        ],
        "Estrutura dos Documentos": [
            "Cabeçalho e identificação",
            "Vocativo e fecho",
            "Corpo do texto e numeração",
        ],
        "Normas do Manual de Redação da Presidência": [
            "Pronome de tratamento",
            "Fechos de comunicações",
            "Siglas e abreviaturas",
        ],
    },

    "Raciocínio Lógico-Matemático": {
        "Lógica Proposicional": [
            "Proposições simples e compostas",
            "Conectivos lógicos (e, ou, se...então, sse)",
            "Tabelas-verdade",
            "Tautologia, contradição e contingência",
            "Negação de proposições compostas",
        ],
        "Lógica de Argumentação": [
            "Validade de argumentos",
            "Silogismo categórico",
            "Inferência e dedução",
        ],
        "Teoria dos Conjuntos": [
            "Operações (união, interseção, diferença)",
            "Diagramas de Venn",
            "Pertinência e inclusão",
        ],
        "Sequências e Progressões": [
            "Progressão Aritmética (PA)",
            "Progressão Geométrica (PG)",
            "Sequências lógicas numéricas e figurativas",
        ],
        "Combinatória e Probabilidade": [
            "Princípio fundamental da contagem",
            "Permutação, arranjo e combinação",
            "Probabilidade simples e condicional",
        ],
        "Raciocínio Quantitativo": [
            "Porcentagem e variação percentual",
            "Razão e proporção",
            "Regra de três simples e composta",
            "Problemas de mistura",
        ],
    },

    "Matemática Financeira": {
        "Juros Simples": [
            "Montante e capital",
            "Taxa e prazo",
            "Desconto simples (comercial e racional)",
        ],
        "Juros Compostos": [
            "Montante e fórmula",
            "Taxa equivalente",
            "Desconto composto",
        ],
        "Séries de Pagamentos": [
            "Anuidades (prestações iguais)",
            "Valor presente e futuro",
            "SAC e PRICE",
        ],
        "Análise de Investimentos": [
            "VPL e TIR",
            "Payback simples e descontado",
        ],
    },

    "Estatística": {
        "Estatística Descritiva": [
            "Média, mediana e moda",
            "Variância e desvio padrão",
            "Quartis e percentis",
        ],
        "Distribuições de Frequência": [
            "Tabelas de frequência",
            "Histograma e polígono",
            "Amplitude e classes",
        ],
        "Probabilidade Estatística": [
            "Espaço amostral",
            "Distribuição binomial",
            "Distribuição normal",
        ],
        "Correlação e Regressão": [
            "Coeficiente de correlação",
            "Regressão linear simples",
        ],
    },

    "Noções de Informática": {
        "Hardware e Software": [
            "Componentes do computador",
            "Sistemas operacionais (Windows, Linux)",
            "Licenças de software",
        ],
        "Internet e Redes": [
            "Protocolos (HTTP, HTTPS, FTP, SMTP)",
            "Navegadores e mecanismos de busca",
            "Redes LAN, WAN, Wi-Fi",
            "IP, DNS e servidores",
        ],
        "Segurança Básica": [
            "Vírus, trojans e malware",
            "Phishing e engenharia social",
            "Backup e antivírus",
        ],
        "Pacote Office / LibreOffice": [
            "Editor de textos (Word)",
            "Planilha eletrônica (Excel)",
            "Apresentações (PowerPoint)",
        ],
        "Correio Eletrônico": [
            "Protocolos de e-mail (POP3, IMAP, SMTP)",
            "Boas práticas e etiqueta",
        ],
        "Armazenamento em Nuvem": [
            "Conceitos de cloud computing",
            "OneDrive, Google Drive, Dropbox",
        ],
    },

    "Segurança da Informação": {
        "Fundamentos": [
            "CID: Confidencialidade, Integridade, Disponibilidade",
            "Autenticação e autorização",
            "Não-repúdio",
        ],
        "Criptografia": [
            "Criptografia simétrica e assimétrica",
            "Certificado digital e PKI",
            "Hash e assinatura digital",
        ],
        "Ameaças e Ataques": [
            "Malware (vírus, ransomware, spyware)",
            "Ataques de negação de serviço (DoS/DDoS)",
            "SQL Injection e XSS",
            "Engenharia social e phishing",
        ],
        "Controles e Políticas": [
            "Política de segurança da informação",
            "ISO 27001 / 27002",
            "Gestão de riscos",
        ],
        "LGPD": [
            "Princípios e bases legais",
            "Direitos do titular",
            "ANPD e sanções",
        ],
    },

    "Ética no Serviço Público": {
        "Ética e Moral": [
            "Conceitos e distinções",
            "Ética individual e profissional",
            "Virtudes e deveres funcionais",
        ],
        "Código de Ética do Servidor (Dec. 1.171/94)": [
            "Regras deontológicas",
            "Deveres e proibições",
            "Comissões de Ética",
        ],
        "Lei Anticorrupção (Lei 12.846/13)": [
            "Responsabilização de pessoas jurídicas",
            "Atos lesivos à Administração",
            "Acordos de leniência",
        ],
        "Improbidade Administrativa (Lei 8.429/92)": [
            "Atos de enriquecimento ilícito",
            "Atos que causam dano ao erário",
            "Atos que atentam contra princípios",
            "Sanções",
        ],
        "Conflito de Interesses (Lei 12.813/13)": [
            "Situações de conflito",
            "Impedimentos e vedações",
        ],
    },

    "Atualidades": {
        "Política Nacional": [
            "Poderes da República",
            "Eleições e partidos",
            "Reformas e legislação recente",
        ],
        "Economia Brasileira": [
            "Indicadores (IPCA, PIB, taxa Selic)",
            "Política fiscal e monetária",
            "Comércio exterior",
        ],
        "Relações Internacionais": [
            "Organismos internacionais (ONU, OMC, FMI)",
            "Acordos e tratados",
            "Geopolítica contemporânea",
        ],
        "Ciência e Tecnologia": [
            "Inovações tecnológicas",
            "Inteligência Artificial aplicada",
            "Meio ambiente e COP",
        ],
        "Temas Sociais": [
            "Saúde pública (pandemias, SUS)",
            "Educação e desigualdade",
            "Segurança pública",
        ],
    },

    "Realidade Brasileira": {
        "Geografia do Brasil": [
            "Regiões, estados e capitais",
            "Relevo, clima e hidrografia",
            "Biomas brasileiros",
        ],
        "História do Brasil": [
            "Período colonial",
            "Independência e Império",
            "República Velha e Era Vargas",
            "Ditadura Militar e redemocratização",
        ],
        "Economia e Desenvolvimento": [
            "Matriz produtiva",
            "Infraestrutura e logística",
            "Desigualdades regionais",
        ],
    },

    "Diversidade e Inclusão": {
        "Direitos das Minorias": [
            "Pessoas com deficiência (Lei 13.146/15)",
            "Igualdade racial (Lei 12.288/10)",
            "Direitos LGBTQIA+",
        ],
        "Políticas de Inclusão": [
            "Cotas raciais e sociais",
            "Acessibilidade",
            "Educação inclusiva",
        ],
    },

    "Sustentabilidade e Meio Ambiente": {
        "Legislação Ambiental": [
            "Código Florestal (Lei 12.651/12)",
            "PNMA (Lei 6.938/81)",
            "Crimes ambientais (Lei 9.605/98)",
        ],
        "Gestão Ambiental": [
            "Licenciamento ambiental",
            "EIA/RIMA",
            "SISNAMA",
        ],
        "Desenvolvimento Sustentável": [
            "ODS — Agenda 2030",
            "Economia circular",
            "Mudanças climáticas e Acordo de Paris",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # JURÍDICAS (DIREITO)
    # ══════════════════════════════════════════════════════════════════════════

    "Direito Constitucional": {
        "Princípios Fundamentais": [
            "Fundamentos da República (art. 1º)",
            "Objetivos fundamentais (art. 3º)",
            "Princípios das relações internacionais",
        ],
        "Direitos e Garantias Fundamentais": [
            "Direitos individuais e coletivos (art. 5º)",
            "Direitos sociais (arts. 6º-11)",
            "Direitos políticos (arts. 14-16)",
            "Remédios constitucionais (HC, MS, MI, HD, AP)",
        ],
        "Organização do Estado": [
            "Forma de Estado e de governo",
            "Organização político-administrativa",
            "Competências da União, estados e municípios",
        ],
        "Poder Legislativo": [
            "Congresso Nacional, Câmara e Senado",
            "Processo legislativo",
            "Imunidades parlamentares",
        ],
        "Poder Executivo": [
            "Presidente e atribuições",
            "Ministros e Conselho de Ministros",
            "Medidas Provisórias",
        ],
        "Poder Judiciário": [
            "Estrutura e competências",
            "STF, STJ, TST, TSE, STM",
            "Garantias da magistratura",
        ],
        "Controle de Constitucionalidade": [
            "Controle difuso e concentrado",
            "ADI, ADC, ADPF",
            "Efeitos das decisões",
        ],
        "Ordem Econômica e Social": [
            "Princípios da ordem econômica",
            "Ordem social e seguridade",
            "Educação, saúde e meio ambiente",
        ],
    },

    "Direito Administrativo": {
        "Princípios do Direito Administrativo": [
            "LIMPE (legalidade, impessoalidade, moralidade, publicidade, eficiência)",
            "Princípios implícitos (razoabilidade, proporcionalidade, segurança jurídica)",
            "Supremacia e indisponibilidade do interesse público",
        ],
        "Poderes Administrativos": [
            "Poder vinculado e discricionário",
            "Poder hierárquico",
            "Poder disciplinar",
            "Poder regulamentar",
            "Poder de polícia",
        ],
        "Atos Administrativos": [
            "Conceito, requisitos e elementos",
            "Atributos (presunção de legitimidade, imperatividade, autoexecutoriedade)",
            "Classificação dos atos",
            "Extinção (revogação, anulação, cassação, caducidade)",
            "Convalidação",
        ],
        "Organização da Administração Pública": [
            "Administração direta",
            "Autarquias e fundações públicas",
            "Empresas públicas e sociedades de economia mista",
            "Consórcios públicos",
        ],
        "Serviços Públicos": [
            "Conceito e princípios",
            "Concessão e permissão",
            "Autorização",
        ],
        "Licitações e Contratos (Lei 14.133/21)": [
            "Princípios e modalidades",
            "Fases da licitação",
            "Dispensa e inexigibilidade",
            "Contratos administrativos: cláusulas e alteração",
            "Extinção e sanções contratuais",
        ],
        "Servidores Públicos (Lei 8.112/90)": [
            "Cargo, emprego e função",
            "Provimento e vacância",
            "Direitos e vantagens",
            "Deveres e proibições",
            "Responsabilidades e penalidades",
            "Processo administrativo disciplinar (PAD)",
        ],
        "Controle da Administração": [
            "Controle interno e externo",
            "Controle pelo Legislativo e TCU",
            "Controle judicial",
        ],
        "Responsabilidade Civil do Estado": [
            "Teoria objetiva (risco administrativo)",
            "Excludentes de responsabilidade",
            "Ação regressiva",
        ],
        "Processo Administrativo (Lei 9.784/99)": [
            "Princípios e aplicação",
            "Direitos do administrado",
            "Prazos e recursos",
        ],
    },

    "Direito Civil": {
        "Lei de Introdução às Normas do Direito Brasileiro": [
            "Vigência e eficácia",
            "Conflito de leis no tempo e no espaço",
        ],
        "Pessoas": [
            "Pessoa natural: capacidade e personalidade",
            "Pessoa jurídica: tipos e registro",
            "Domicílio",
        ],
        "Bens": [
            "Classificação dos bens",
            "Bens públicos e privados",
        ],
        "Fatos e Negócios Jurídicos": [
            "Classificação dos fatos jurídicos",
            "Requisitos de validade",
            "Vícios do negócio jurídico",
            "Nulidade e anulabilidade",
        ],
        "Obrigações": [
            "Modalidades de obrigações",
            "Adimplemento e extinção",
            "Inadimplemento e mora",
        ],
        "Contratos": [
            "Princípios contratuais",
            "Contratos em espécie (compra e venda, locação, doação...)",
            "Extinção dos contratos",
        ],
        "Responsabilidade Civil": [
            "Elementos: conduta, dano, nexo causal, culpa",
            "Responsabilidade subjetiva e objetiva",
            "Dano moral e material",
        ],
        "Família": [
            "Casamento e união estável",
            "Filiação e reconhecimento",
            "Alimentos e guarda",
        ],
        "Sucessões": [
            "Sucessão legítima",
            "Sucessão testamentária",
            "Inventário e partilha",
        ],
    },

    "Direito Processual Civil": {
        "Princípios e Normas Fundamentais (CPC/15)": [
            "Contraditório e ampla defesa",
            "Princípio da cooperação",
            "Primazia do julgamento de mérito",
        ],
        "Competência": [
            "Competência absoluta e relativa",
            "Competência territorial e funcional",
            "Conflito de competência",
        ],
        "Partes e Procuradores": [
            "Capacidade processual",
            "Legitimidade e interesse processual",
            "Litisconsórcio e intervenção de terceiros",
        ],
        "Atos Processuais e Prazos": [
            "Forma e lugar dos atos",
            "Comunicação dos atos (citação e intimação)",
            "Prazos e preclusão",
        ],
        "Procedimento Comum": [
            "Petição inicial e emenda",
            "Contestação e reconvenção",
            "Audiência de conciliação",
            "Sentença e coisa julgada",
        ],
        "Recursos": [
            "Apelação",
            "Agravo de instrumento e interno",
            "Embargos de declaração",
            "Recurso especial e extraordinário",
        ],
        "Tutelas Provisórias": [
            "Tutela antecipada e cautelar",
            "Tutela de urgência e evidência",
        ],
        "Execução": [
            "Título executivo judicial e extrajudicial",
            "Penhora e avaliação",
            "Embargos à execução",
        ],
    },

    "Direito Penal": {
        "Princípios": [
            "Legalidade, anterioridade, retroatividade benéfica",
            "Intervenção mínima e fragmentariedade",
            "Culpabilidade e proporcionalidade",
        ],
        "Teoria do Crime": [
            "Conduta, tipicidade, ilicitude, culpabilidade",
            "Crimes dolosos e culposos",
            "Tentativa e consumação",
            "Concurso de pessoas",
            "Concurso de crimes",
        ],
        "Causas Excludentes": [
            "Excludentes de tipicidade",
            "Estado de necessidade e legítima defesa",
            "Excludentes de culpabilidade",
        ],
        "Crimes em Espécie (CP)": [
            "Crimes contra a vida (arts. 121-128)",
            "Crimes contra o patrimônio (arts. 155-183)",
            "Crimes contra a Administração Pública (arts. 312-359)",
            "Crimes contra a fé pública",
        ],
        "Penas e Aplicação": [
            "Espécies de pena",
            "Dosimetria (circunstâncias judiciais, atenuantes, agravantes)",
            "Penas restritivas de direitos",
            "Extinção da punibilidade",
        ],
        "Legislação Penal Especial": [
            "Lei de Drogas (11.343/06)",
            "Lei de Tortura (9.455/97)",
            "Lei de Lavagem de Dinheiro (9.613/98)",
            "Lei de Abuso de Autoridade (13.869/19)",
        ],
    },

    "Direito Processual Penal": {
        "Princípios e Inquérito Policial": [
            "Inquisitoriedade do inquérito",
            "Procedimento e prazo",
            "Arquivamento",
        ],
        "Ação Penal": [
            "Pública incondicionada e condicionada",
            "Ação privada",
            "Condições da ação",
        ],
        "Competência": [
            "Ratione materiae e ratione personae",
            "Foro privilegiado",
            "Conflito de competência",
        ],
        "Provas": [
            "Ônus da prova e inadmissibilidade",
            "Prova ilícita",
            "Provas em espécie (documental, testemunhal, pericial)",
        ],
        "Prisão e Liberdade": [
            "Prisão em flagrante",
            "Prisão preventiva e temporária",
            "Liberdade provisória e fiança",
            "Medidas cautelares diversas",
        ],
        "Procedimentos": [
            "Procedimento ordinário e sumário",
            "Júri popular",
            "Juizados Especiais Criminais (9.099/95)",
        ],
        "Recursos": [
            "Recurso em sentido estrito",
            "Apelação criminal",
            "Habeas corpus e revisão criminal",
        ],
    },

    "Direito Tributário": {
        "Sistema Tributário Nacional": [
            "Competência tributária",
            "Limitações constitucionais ao poder de tributar",
            "Imunidades e isenções",
        ],
        "Obrigação Tributária": [
            "Fato gerador",
            "Sujeitos ativo e passivo",
            "Solidariedade e responsabilidade tributária",
        ],
        "Crédito Tributário": [
            "Constituição (lançamento)",
            "Suspensão do crédito",
            "Extinção (pagamento, prescrição, decadência)",
            "Exclusão (isenção e anistia)",
        ],
        "Tributos em Espécie": [
            "Impostos federais (IR, IPI, IOF, II, IE)",
            "ICMS e ISS",
            "IPVA e IPTU",
            "Contribuições (PIS, COFINS, CSLL)",
        ],
        "Processo Tributário": [
            "Consulta fiscal",
            "Processo administrativo fiscal",
            "Execução fiscal",
        ],
        "CTN — Código Tributário Nacional": [
            "Disposições gerais",
            "Legislação tributária",
            "Interpretação e integração",
        ],
    },

    "Direito do Trabalho": {
        "Princípios e Fontes": [
            "Princípios protetivos",
            "Fontes formais e materiais",
            "CLT e legislação complementar",
        ],
        "Contrato de Trabalho": [
            "Formação e requisitos",
            "Modalidades (prazo indeterminado, determinado, intermitente)",
            "Alteração e suspensão",
        ],
        "Jornada de Trabalho": [
            "Duração e horas extras",
            "Turnos e compensações",
            "Trabalho noturno",
        ],
        "Remuneração": [
            "Salário mínimo e piso salarial",
            "Adicionais (insalubridade, periculosidade, noturno)",
            "13º salário e participação nos lucros",
        ],
        "Férias e FGTS": [
            "Concessão e pagamento de férias",
            "FGTS: recolhimento e saque",
        ],
        "Rescisão Contratual": [
            "Demissão sem justa causa",
            "Demissão por justa causa",
            "Pedido de demissão e rescisão indireta",
            "Aviso prévio",
        ],
        "Seguridade e Previdência Trabalhista": [
            "Estabilidade e garantias de emprego",
            "Licença maternidade e paternidade",
            "Acidente de trabalho",
        ],
    },

    "Direito Processual do Trabalho": {
        "Organização da Justiça do Trabalho": [
            "Varas, TRT e TST",
            "Competência",
        ],
        "Ação Trabalhista": [
            "Reclamação trabalhista",
            "Prazo prescricional",
            "Dissídio coletivo",
        ],
        "Provas e Audiências": [
            "Ônus da prova",
            "Prova testemunhal e documental",
            "Audiências e julgamento",
        ],
        "Execução Trabalhista": [
            "Título executivo",
            "Cálculo e liquidação",
            "Penhora e expropriação",
        ],
    },

    "Direito Eleitoral": {
        "Sistemas Eleitorais": [
            "Maioritário, proporcional e misto",
            "Quociente eleitoral e partidário",
        ],
        "Alistamento e Domicílio Eleitoral": [
            "Obrigatoriedade e alistamento",
            "Cancelamento do título",
        ],
        "Candidaturas": [
            "Condições de elegibilidade",
            "Inelegibilidades (Lei Ficha Limpa)",
            "Registro de candidatura",
        ],
        "Crimes Eleitorais": [
            "Captação ilícita de sufrágio",
            "Corrupção eleitoral",
        ],
    },

    "Direito Previdenciário": {
        "Seguridade Social": [
            "Saúde, previdência e assistência social",
            "Princípios constitucionais",
            "Custeio (contribuições)",
        ],
        "Regime Geral de Previdência (RGPS)": [
            "Segurados obrigatórios e facultativos",
            "Salário de contribuição",
            "Carência",
        ],
        "Benefícios Previdenciários": [
            "Aposentadorias (programada, por incapacidade)",
            "Auxílios (doença, acidente)",
            "Salário-família e salário-maternidade",
            "Pensão por morte",
        ],
        "Regime Próprio (RPPS)": [
            "Servidores públicos",
            "Reforma da Previdência (EC 103/19)",
        ],
    },

    "Direito Ambiental": {
        "Princípios": [
            "Precaução e prevenção",
            "Poluidor-pagador",
            "Desenvolvimento sustentável",
        ],
        "Política Nacional do Meio Ambiente (PNMA)": [
            "Objetivos e instrumentos",
            "SISNAMA e CONAMA",
            "Licenciamento ambiental",
        ],
        "Código Florestal (Lei 12.651/12)": [
            "APP e Reserva Legal",
            "Uso restrito e consolidado",
            "CAR e PRA",
        ],
        "Responsabilidade Ambiental": [
            "Responsabilidade civil objetiva",
            "Crimes ambientais (Lei 9.605/98)",
            "Sanções administrativas",
        ],
    },

    "Direito do Consumidor": {
        "Princípios e Direitos Básicos (CDC)": [
            "Vulnerabilidade do consumidor",
            "Boa-fé objetiva e transparência",
            "Direitos básicos (art. 6º)",
        ],
        "Responsabilidade pelo Fato e Vício": [
            "Fato do produto e serviço",
            "Vício do produto e serviço",
            "Excludentes de responsabilidade",
        ],
        "Práticas Comerciais": [
            "Publicidade enganosa e abusiva",
            "Cláusulas abusivas",
            "Cobrança de dívidas",
        ],
        "Proteção Contratual": [
            "Contrato de adesão",
            "Prazo de reflexão",
        ],
        "Defesa do Consumidor": [
            "PROCON e órgãos de defesa",
            "Ações coletivas",
        ],
    },

    "Direitos Humanos": {
        "Fundamentos e Geração de Direitos": [
            "Universalidade e indivisibilidade",
            "Gerações (1ª, 2ª, 3ª e 4ª)",
        ],
        "Sistemas de Proteção": [
            "Sistema ONU (PIDCP, PIDESC)",
            "Sistema Interamericano (CADH, CIDH, Corte IDH)",
        ],
        "Direitos na Constituição Federal": [
            "Direitos individuais e coletivos",
            "Direitos sociais",
            "Incorporação de tratados (§3º, art. 5º)",
        ],
        "Grupos Vulneráveis": [
            "Crianças e adolescentes",
            "Mulheres e violência doméstica",
            "Pessoas com deficiência",
            "Migrantes e refugiados",
        ],
    },

    "Legislação Extravagante": {
        "Lei de Improbidade (8.429/92)": [
            "Sujeitos ativo e passivo",
            "Atos de improbidade e sanções",
            "Prescrição",
        ],
        "Lei de Responsabilidade Fiscal (LC 101/00)": [
            "Planejamento e transparência",
            "Receita e despesa",
            "Dívida pública",
        ],
        "Lei de Acesso à Informação (12.527/11)": [
            "Transparência ativa e passiva",
            "Sigilo e restrições",
            "Recursos e penalidades",
        ],
        "LGPD (13.709/18)": [
            "Princípios e bases legais",
            "Direitos do titular",
            "ANPD e sanções",
        ],
    },

    "Estatuto da Criança e do Adolescente (ECA)": {
        "Direitos Fundamentais": [
            "Direito à vida e à saúde",
            "Direito à educação e ao esporte",
            "Direito à convivência familiar",
        ],
        "Medidas de Proteção": [
            "Conselho Tutelar",
            "Medidas protetivas (art. 101)",
        ],
        "Ato Infracional": [
            "Apuração do ato infracional",
            "Medidas socioeducativas",
            "Internação",
        ],
        "Adoção": [
            "Cadastro de adoção",
            "Procedimento e prazo",
        ],
    },

    "Estatuto do Idoso": {
        "Direitos Fundamentais": [
            "Direito à saúde e à assistência social",
            "Direito à moradia e transporte",
        ],
        "Medidas de Proteção": [
            "Entidades de atendimento",
            "Curatela e tutela",
        ],
        "Crimes contra o Idoso": [
            "Abandono e maus-tratos",
            "Discriminação",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # GESTÃO E NEGÓCIOS
    # ══════════════════════════════════════════════════════════════════════════

    "Administração Geral": {
        "Fundamentos da Administração": [
            "Teorias clássica e neoclássica",
            "Abordagem sistêmica e contingencial",
            "Funções administrativas (PODC)",
        ],
        "Planejamento": [
            "Planejamento estratégico, tático e operacional",
            "Análise SWOT",
            "BSC — Balanced Scorecard",
        ],
        "Organização": [
            "Estruturas organizacionais",
            "Departamentalização",
            "Amplitude e cadeia de comando",
        ],
        "Gestão de Desempenho": [
            "Indicadores e metas",
            "Avaliação de desempenho",
            "Melhoria contínua (PDCA)",
        ],
        "Liderança e Motivação": [
            "Estilos de liderança",
            "Teorias motivacionais (Maslow, Herzberg, McClelland)",
            "Clima e cultura organizacional",
        ],
    },

    "Administração Pública": {
        "Modelos de Gestão": [
            "Patrimonialismo, burocracia e gerencialismo",
            "Nova Gestão Pública (NGP)",
            "Governança pública",
        ],
        "Estrutura da Administração Federal": [
            "Decreto 9.745/19 e organização ministerial",
            "Órgãos e entidades",
            "Descentralização e desconcentração",
        ],
        "Reforma Administrativa": [
            "Plano Diretor de Reforma do Estado (1995)",
            "Agências reguladoras",
            "Parceria público-privada (PPP)",
        ],
        "Controle": [
            "Controle interno (CGU)",
            "Controle externo (TCU)",
            "Controle social e ouvidorias",
        ],
    },

    "Gestão de Pessoas": {
        "Subsistemas de RH": [
            "Recrutamento e seleção",
            "Treinamento e desenvolvimento",
            "Avaliação de desempenho",
            "Cargos e salários",
        ],
        "Comportamento Organizacional": [
            "Motivação no trabalho",
            "Grupos e equipes",
            "Conflito e negociação",
        ],
        "Gestão Estratégica de Pessoas": [
            "Alinhamento estratégico de RH",
            "Competências essenciais",
            "Gestão por competências",
        ],
    },

    "Gestão de Processos": {
        "BPM — Business Process Management": [
            "Modelagem de processos (BPMN)",
            "Ciclo de vida do processo",
            "Mapeamento AS-IS e TO-BE",
        ],
        "Melhoria de Processos": [
            "Lean e eliminação de desperdícios",
            "Six Sigma",
            "Kaizen",
        ],
        "Ferramentas de Qualidade": [
            "Diagrama de Causa e Efeito (Ishikawa)",
            "Diagrama de Pareto",
            "Fluxograma e 5S",
        ],
    },

    "Gestão de Projetos": {
        "Fundamentos (PMBOK)": [
            "Ciclo de vida do projeto",
            "Grupos de processos",
            "Áreas de conhecimento",
        ],
        "Planejamento": [
            "EAP — Estrutura Analítica do Projeto",
            "Cronograma (Gantt, PERT/CPM)",
            "Gestão de riscos",
        ],
        "Execução e Controle": [
            "Gerenciamento de mudanças",
            "Indicadores (CPI, SPI)",
            "Encerramento do projeto",
        ],
        "Metodologias Ágeis": [
            "Scrum (sprints, papéis, cerimônias)",
            "Kanban",
            "SAFe e escalabilidade",
        ],
    },

    "Administração Financeira e Orçamentária (AFO)": {
        "Orçamento Público": [
            "PPA, LDO e LOA",
            "Princípios orçamentários",
            "Classificação da receita e despesa",
        ],
        "Ciclo Orçamentário": [
            "Elaboração e aprovação",
            "Execução (empenho, liquidação, pagamento)",
            "Controle e avaliação",
        ],
        "Créditos Adicionais": [
            "Suplementares, especiais e extraordinários",
            "Abertura e fontes de recursos",
        ],
        "Receita Pública": [
            "Previsão e arrecadação",
            "Renúncia de receita",
            "Receitas originárias e derivadas",
        ],
        "Despesa Pública": [
            "Dotação e restos a pagar",
            "Despesas de pessoal",
            "Limites de gastos (EC 95)",
        ],
    },

    "Lei de Responsabilidade Fiscal (LRF)": {
        "Equilíbrio Fiscal": [
            "Metas e resultados fiscais",
            "Resultado primário e nominal",
        ],
        "Receitas e Despesas": [
            "Renúncia de receita",
            "Geração de despesa e impacto orçamentário",
            "Despesas com pessoal (limites)",
        ],
        "Dívida e Endividamento": [
            "Dívida consolidada e mobiliária",
            "Limites de endividamento",
            "Operações de crédito",
        ],
        "Transparência e Controle": [
            "Relatório Resumido de Execução Orçamentária (RREO)",
            "Relatório de Gestão Fiscal (RGF)",
            "Audiências públicas",
        ],
    },

    "Licitações e Contratos": {
        "Lei 14.133/21 — Nova Lei de Licitações": [
            "Princípios",
            "Modalidades (pregão, concorrência, concurso, leilão, diálogo competitivo)",
            "Fases da licitação (preparatória, divulgação, propostas, julgamento, habilitação)",
            "Dispensa e inexigibilidade",
        ],
        "Contratos Administrativos": [
            "Cláusulas exorbitantes",
            "Alteração unilateral e bilateral",
            "Equilíbrio econômico-financeiro",
            "Extinção e sanções",
        ],
        "Registro de Preços": [
            "Sistema de Registro de Preços (SRP)",
            "Ata de Registro de Preços",
        ],
    },

    "Arquivologia": {
        "Gestão de Documentos": [
            "Protocolo e tramitação",
            "Classificação de documentos",
            "Tabela de temporalidade",
        ],
        "Ciclo de Vida": [
            "Fase corrente, intermediária e permanente",
            "Destinação: eliminação e recolhimento",
        ],
        "Arquivos Especiais": [
            "Arquivo digital e microfilmagem",
            "Preservação e conservação",
        ],
        "Legislação Arquivística": [
            "Lei 8.159/91",
            "CONARQ e SINAR",
        ],
    },

    "Governança Pública": {
        "Princípios de Governança": [
            "Accountability e transparência",
            "Responsividade e equidade",
        ],
        "Modelos e Ferramentas": [
            "Governança de TI (COBIT, ITIL)",
            "Gestão de riscos (ISO 31000)",
            "Auditoria interna",
        ],
        "Órgãos de Controle": [
            "CGU, TCU e AGU",
            "Ouvidorias",
        ],
    },

    "Políticas Públicas": {
        "Ciclo de Políticas Públicas": [
            "Formação de agenda",
            "Formulação e tomada de decisão",
            "Implementação",
            "Avaliação e monitoramento",
        ],
        "Atores e Arenas": [
            "Stakeholders e grupos de interesse",
            "Coalizões e redes de política",
        ],
        "Avaliação de Políticas": [
            "Avaliação ex-ante e ex-post",
            "Indicadores de resultado e impacto",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # FINANCEIRAS E CONTROLE
    # ══════════════════════════════════════════════════════════════════════════

    "Contabilidade Geral": {
        "Fundamentos": [
            "Patrimônio, ativo e passivo",
            "Equação patrimonial",
            "Fatos contábeis (permutativos, modificativos, mistos)",
        ],
        "Plano de Contas e Escrituração": [
            "Plano de contas",
            "Lançamentos contábeis",
            "Livros contábeis (Diário, Razão)",
        ],
        "Demonstrações Contábeis": [
            "Balanço Patrimonial",
            "DRE — Demonstração de Resultado",
            "DLPA e DFC",
            "Notas explicativas",
        ],
        "Análise das Demonstrações": [
            "Índices de liquidez",
            "Índices de endividamento",
            "Índices de rentabilidade",
        ],
        "NBC e CPC": [
            "Normas Brasileiras de Contabilidade",
            "CPC 00 — Estrutura Conceitual",
            "Principais CPCs",
        ],
    },

    "Contabilidade Pública": {
        "MCASP — Manual de Contabilidade Aplicada ao Setor Público": [
            "Plano de Contas Aplicado ao Setor Público (PCASP)",
            "Receita e despesa orçamentária",
            "Registros contábeis patrimoniais",
        ],
        "Balanços Públicos": [
            "Balanço Orçamentário",
            "Balanço Financeiro",
            "Balanço Patrimonial",
            "Demonstração das Variações Patrimoniais (DVP)",
        ],
        "NBCASP": [
            "NBC T 16 e normas correlatas",
            "Convergência às IPSAS",
        ],
    },

    "Contabilidade de Custos": {
        "Fundamentos de Custos": [
            "Conceito e classificação (fixo, variável, direto, indireto)",
            "Custeio por absorção",
            "Custeio variável (direto)",
        ],
        "Análise Custo-Volume-Lucro": [
            "Ponto de equilíbrio",
            "Margem de contribuição",
            "Alavancagem operacional",
        ],
        "Custeio ABC": [
            "Atividades e direcionadores",
            "Aplicação no setor público",
        ],
    },

    "Auditoria Governamental": {
        "Tipos de Auditoria": [
            "Auditoria de conformidade",
            "Auditoria operacional",
            "Auditoria de gestão",
        ],
        "Planejamento e Execução": [
            "Risco de auditoria",
            "Materialidade e relevância",
            "Evidências e papéis de trabalho",
        ],
        "Controle Interno": [
            "Componentes do COSO",
            "Gestão de riscos integrada",
        ],
        "TCU e CGU": [
            "Competências constitucionais do TCU",
            "Atuação da CGU",
        ],
    },

    "Economia (Micro e Macro)": {
        "Microeconomia": [
            "Teoria do consumidor (demanda)",
            "Teoria da firma (oferta)",
            "Estruturas de mercado",
            "Elasticidades",
        ],
        "Macroeconomia": [
            "PIB e contas nacionais",
            "Inflação e índices de preços",
            "Política monetária e fiscal",
            "Balanço de pagamentos",
        ],
        "Teoria Econômica": [
            "Externalidades e bens públicos",
            "Falhas de mercado",
        ],
    },

    "Comércio Internacional": {
        "Teoria do Comércio": [
            "Vantagem comparativa e absoluta",
            "Política comercial (tarifas, quotas)",
        ],
        "Organismos Internacionais": [
            "OMC — Organização Mundial do Comércio",
            "MERCOSUL e acordos regionais",
        ],
        "Câmbio": [
            "Taxa de câmbio nominal e real",
            "Regimes cambiais",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # TECNOLOGIA E DADOS
    # ══════════════════════════════════════════════════════════════════════════

    "Banco de Dados": {
        "Fundamentos": [
            "Modelo relacional",
            "Entidade-Relacionamento (ER)",
            "Normalização (1FN, 2FN, 3FN, BCNF)",
        ],
        "SQL": [
            "DDL (CREATE, ALTER, DROP)",
            "DML (SELECT, INSERT, UPDATE, DELETE)",
            "JOINs e subconsultas",
            "Funções de agregação",
        ],
        "Administração": [
            "Transações e ACID",
            "Índices e otimização",
            "Backup e recuperação",
        ],
        "Bancos NoSQL": [
            "Tipos (chave-valor, documento, coluna, grafo)",
            "MongoDB, Redis, Cassandra",
            "CAP Theorem",
        ],
    },

    "Engenharia de Software": {
        "Processos de Software": [
            "Cascata, incremental e espiral",
            "Metodologias ágeis (Scrum, XP, Kanban)",
            "DevOps",
        ],
        "Requisitos": [
            "Levantamento e análise",
            "Casos de uso e histórias de usuário",
            "Rastreabilidade",
        ],
        "Arquitetura de Software": [
            "Padrões arquiteturais (MVC, microsserviços)",
            "Padrões de projeto (GoF)",
            "REST e SOA",
        ],
        "Qualidade e Testes": [
            "Testes unitários, integração e sistema",
            "TDD e BDD",
            "Métricas de qualidade (CMMI, MPS-BR)",
        ],
    },

    "Linguagens de Programação": {
        "Conceitos Gerais": [
            "Paradigmas (imperativo, OO, funcional)",
            "Compilação vs. interpretação",
            "Tipagem estática e dinâmica",
        ],
        "Orientação a Objetos": [
            "Encapsulamento, herança e polimorfismo",
            "Interfaces e classes abstratas",
            "SOLID",
        ],
        "Estruturas de Dados e Algoritmos": [
            "Listas, pilhas, filas e árvores",
            "Algoritmos de ordenação e busca",
            "Complexidade (Big O)",
        ],
    },

    "Ciência de Dados e Analytics": {
        "Fundamentos": [
            "Processo KDD e CRISP-DM",
            "Tipos de dados e ETL",
        ],
        "Aprendizado de Máquina": [
            "Supervisionado, não-supervisionado e por reforço",
            "Regressão, classificação e clustering",
            "Overfitting, underfitting e validação",
        ],
        "Visualização de Dados": [
            "Gráficos e dashboards",
            "BI — Business Intelligence",
            "Power BI e Tableau",
        ],
        "Big Data": [
            "5 Vs (Volume, Velocidade, Variedade, Veracidade, Valor)",
            "Hadoop e Spark",
        ],
    },

    "Inteligência Artificial": {
        "Fundamentos": [
            "Histórico e conceitos",
            "Agentes inteligentes",
            "Busca e resolução de problemas",
        ],
        "Machine Learning": [
            "Algoritmos supervisionados",
            "Redes neurais e deep learning",
            "NLP — Processamento de linguagem natural",
        ],
        "Ética em IA": [
            "Viés e discriminação",
            "Explicabilidade (XAI)",
            "Regulação de IA",
        ],
    },

    "Governança de TI": {
        "COBIT": [
            "Princípios do COBIT 2019",
            "Objetivos de governança e gestão",
            "Cascata de metas",
        ],
        "ITIL": [
            "Cadeia de valor de serviço",
            "Práticas de ITIL 4",
            "Gerenciamento de incidentes e mudanças",
        ],
        "Segurança e Gestão de Riscos": [
            "ISO 27001 — SGSI",
            "ISO 31000 — Gestão de riscos",
            "NIST Cybersecurity Framework",
        ],
        "Planejamento Estratégico de TI": [
            "PDTI — Plano Diretor de TI",
            "Indicadores de TI",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SAÚDE E EDUCAÇÃO
    # ══════════════════════════════════════════════════════════════════════════

    "Saúde Pública (SUS)": {
        "Fundamentos do SUS": [
            "Princípios doutrinários (universalidade, integralidade, equidade)",
            "Princípios organizativos (descentralização, hierarquização, participação)",
        ],
        "Legislação do SUS": [
            "Lei 8.080/90 (organização do SUS)",
            "Lei 8.142/90 (controle social)",
            "NOB e NOAS",
        ],
        "Atenção à Saúde": [
            "Atenção Básica (AB) e ESF",
            "Atenção especializada e hospitalar",
            "Urgência e emergência (RUE)",
        ],
        "Vigilâncias em Saúde": [
            "Vigilância epidemiológica",
            "Vigilância sanitária (ANVISA)",
            "Vigilância ambiental em saúde",
        ],
        "Políticas de Saúde": [
            "PNAB — Política Nacional de Atenção Básica",
            "PMAQ e QualiAB",
            "Saúde mental (CAPS)",
        ],
    },

    "Vigilância Sanitária": {
        "Fundamentos": [
            "Conceito e base legal (Lei 9.782/99)",
            "ANVISA e vigilâncias estaduais e municipais",
        ],
        "Inspeção e Fiscalização": [
            "Alimentos e medicamentos",
            "Cosméticos e saneantes",
            "Serviços de saúde",
        ],
        "Registro e Autorização": [
            "Registro de produtos",
            "Licença sanitária",
            "Boas práticas de fabricação",
        ],
    },

    "Conhecimentos Pedagógicos": {
        "Teorias da Aprendizagem": [
            "Behaviorismo (Pavlov, Skinner)",
            "Construtivismo (Piaget)",
            "Sociointeracionismo (Vygotsky)",
            "Aprendizagem significativa (Ausubel)",
        ],
        "Didática e Metodologias": [
            "Planejamento de ensino",
            "Avaliação da aprendizagem",
            "Metodologias ativas",
        ],
        "Currículo": [
            "BNCC",
            "Organização curricular",
            "PCN e DCN",
        ],
        "Educação Inclusiva": [
            "Legislação (Lei 13.146/15)",
            "Adaptações curriculares",
            "AEE — Atendimento Educacional Especializado",
        ],
    },

    "Legislação Educacional (LDB)": {
        "LDB (Lei 9.394/96)": [
            "Princípios e fins da educação",
            "Organização da educação nacional",
            "Níveis e modalidades",
        ],
        "Educação Básica": [
            "Educação Infantil",
            "Ensino Fundamental",
            "Ensino Médio e reforma",
        ],
        "Educação Superior": [
            "Organização e avaliação",
            "SINAES e ENADE",
        ],
        "Profissionais da Educação": [
            "Formação de professores",
            "Piso salarial (Lei 11.738/08)",
            "Plano de Carreira",
        ],
    },
}


# ── Matérias por área ──────────────────────────────────────────────────────────

MATERIAS_POR_AREA: dict = {
    "fiscal": [
        "Língua Portuguesa",
        "Redação Oficial",
        "Raciocínio Lógico-Matemático",
        "Matemática Financeira",
        "Estatística",
        "Noções de Informática",
        "Ética no Serviço Público",
        "Atualidades",
        "Direito Constitucional",
        "Direito Administrativo",
        "Direito Tributário",
        "Administração Pública",
        "Administração Financeira e Orçamentária (AFO)",
        "Lei de Responsabilidade Fiscal (LRF)",
        "Licitações e Contratos",
        "Contabilidade Geral",
        "Contabilidade Pública",
    ],
    "juridica": [
        "Língua Portuguesa",
        "Raciocínio Lógico-Matemático",
        "Direito Constitucional",
        "Direito Administrativo",
        "Direito Civil",
        "Direito Processual Civil",
        "Direito Penal",
        "Direito Processual Penal",
        "Direito Tributário",
        "Direito do Trabalho",
        "Direito Processual do Trabalho",
        "Direitos Humanos",
        "Legislação Extravagante",
        "Ética no Serviço Público",
        "Estatuto da Criança e do Adolescente (ECA)",
        "Estatuto do Idoso",
    ],
    "policial": [
        "Língua Portuguesa",
        "Redação Oficial",
        "Raciocínio Lógico-Matemático",
        "Direito Constitucional",
        "Direito Administrativo",
        "Direito Penal",
        "Direito Processual Penal",
        "Direitos Humanos",
        "Ética no Serviço Público",
        "Noções de Informática",
        "Atualidades",
        "Estatuto da Criança e do Adolescente (ECA)",
        "Realidade Brasileira",
        "Diversidade e Inclusão",
    ],
    "ti": [
        "Língua Portuguesa",
        "Raciocínio Lógico-Matemático",
        "Noções de Informática",
        "Segurança da Informação",
        "Banco de Dados",
        "Engenharia de Software",
        "Linguagens de Programação",
        "Ciência de Dados e Analytics",
        "Inteligência Artificial",
        "Governança de TI",
        "Ética no Serviço Público",
        "Administração Pública",
    ],
    "saude": [
        "Língua Portuguesa",
        "Raciocínio Lógico-Matemático",
        "Noções de Informática",
        "Ética no Serviço Público",
        "Saúde Pública (SUS)",
        "Vigilância Sanitária",
        "Atualidades",
        "Direito Administrativo",
        "Sustentabilidade e Meio Ambiente",
    ],
    "outro": [
        "Língua Portuguesa",
        "Raciocínio Lógico-Matemático",
        "Administração Geral",
        "Administração Pública",
        "Gestão de Pessoas",
        "Gestão de Processos",
        "Gestão de Projetos",
        "Administração Financeira e Orçamentária (AFO)",
        "Lei de Responsabilidade Fiscal (LRF)",
        "Licitações e Contratos",
        "Arquivologia",
        "Governança Pública",
        "Políticas Públicas",
        "Contabilidade Geral",
        "Contabilidade Pública",
        "Auditoria Governamental",
        "Economia (Micro e Macro)",
        "Ética no Serviço Público",
        "Atualidades",
    ],
}


# ── Funções de acesso ──────────────────────────────────────────────────────────

def get_topicos(materia: str) -> list:
    """Retorna a lista de tópicos de uma matéria."""
    return list(HIERARQUIA.get(materia, {}).keys())


def get_subtopicos(materia: str, topico: str) -> list:
    """Retorna a lista de subtópicos de um tópico de uma matéria."""
    return HIERARQUIA.get(materia, {}).get(topico, [])


def get_todas_materias() -> list:
    """Retorna todas as matérias da hierarquia, em ordem alfabética."""
    return sorted(HIERARQUIA.keys())
