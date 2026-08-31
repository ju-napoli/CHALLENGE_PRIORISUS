# PrioriSUS

Projeto acadêmico desenvolvido para o Challenge da FIAP com foco na análise
da infraestrutura de saúde dos municípios brasileiros.

## Objetivo

O projeto busca integrar dados públicos de saúde e população para gerar
indicadores que permitam analisar diferenças na disponibilidade de
infraestrutura de saúde entre municípios.

## Dados utilizados

Foram utilizadas bases públicas contendo informações sobre:

- População municipal
- Unidades Básicas de Saúde (UBS)
- Leitos hospitalares

## Processamento dos dados

A etapa inicial do projeto foi desenvolvida em Python, utilizando Pandas
para:

- exploração e validação das bases;
- tratamento e padronização dos dados;
- integração das informações por código IBGE;
- agregação dos dados por município;
- cálculo de indicadores de disponibilidade de UBS e leitos SUS.

## Indicadores

Atualmente, foram calculados:

- UBS por 10 mil habitantes;
- Leitos SUS por 10 mil habitantes;
- indicadores normalizados para composição do índice do projeto.

A metodologia final do índice será documentada após a validação da lógica
de cálculo.

## Limitações conhecidas

### Tratamento assimétrico de dados ausentes

As duas bases de infraestrutura têm ausências de natureza diferente, e o
pipeline as trata de forma deliberadamente diferente.

**Leitos SUS — ausência é tratada como zero.** A base de leitos é um cadastro
de estabelecimentos que possuem leitos: nenhuma linha da competência utilizada
tem `LEITOS_EXISTENTES == 0`, e todos os tipos de unidade são hospitais,
unidades mistas ou prontos-socorros. Um município ausente dessa base não é um
município cujo número de leitos é desconhecido — é um município sem nenhum
estabelecimento com leito. A ausência, portanto, é informação, e recebe
`fillna(0)`. Manter esses 2.013 municípios como dado faltante produzia uma
contradição: municípios com zero leitos explicitamente registrado recebiam
déficit máximo e iam ao topo do ranking, enquanto municípios na mesma situação
de fato, porém ausentes da base, eram descartados do ranking inteiro.

**UBS — ausência é sinalizada, não preenchida.** Os 83 municípios sem
correspondência na base de UBS são tratados como lacuna de cadastro, e não
como ausência real de unidades básicas. A evidência é que 46 deles possuem
hospital com leitos SUS registrados no CNES; o maior, Araruama/RJ, tem 137.906
habitantes, 4 estabelecimentos hospitalares e 186 leitos SUS — é implausível
que não tenha nenhuma UBS. Preencher com zero daria prioridade máxima de
investimento a municípios cujo problema é o registro, não a infraestrutura.
Esses municípios permanecem no ranking com a coluna `DADO_UBS_AUSENTE = True`,
e seu IPIS é calculado apenas sobre o déficit de leitos.

**Como ler o resultado:** as linhas com `DADO_UBS_AUSENTE = True` apoiam-se em
um único componente do índice e são menos comparáveis com as demais. As
colunas `QTD_UBS`, `UBS_POR_10MIL` e `DEFICIT_UBS` ficam vazias nesses casos.

### Ausência de acessibilidade regional

O índice mede a infraestrutura existente **dentro do território municipal**, e
não a infraestrutura **acessível** à população daquele município.

Essa distinção importa porque o SUS é organizado de forma regionalizada: pelo
Plano Diretor de Regionalização, municípios de pequeno porte não são
projetados para ter hospital próprio — são referenciados a um polo regional.
Um município de 2 mil habitantes sem leitos no próprio território pode estar
adequadamente atendido por um hospital a 30 km de distância.

O efeito prático é concentrado no topo do ranking: os 37 municípios que
aparecem empatados com IPIS = 100,00 não possuem nenhuma das duas
infraestruturas localmente, mas **não é possível afirmar, com os dados atuais,
que sejam os mais carentes do país**. Podem estar corretamente referenciados a
um polo regional. O índice sinaliza ausência local de infraestrutura, o que é
uma pergunta legítima e bem medida, mas ainda não responde "onde há população
sem acesso a infraestrutura de saúde", que é a pergunta de política pública.

Resolver isso exige incorporar a região de saúde como unidade de análise
(leitos SUS disponíveis na região, distância ao estabelecimento mais próximo)
e está fora do escopo da versão atual.

### Outras limitações

- **Faixas relativas.** `FAIXA_IPIS` usa os tercis da distribuição observada,
  não cortes absolutos. "Alta prioridade" significa "no terço mais carente
  desta base" e os cortes se deslocam a cada atualização dos dados. Os valores
  utilizados são impressos pelo script 05 e devem acompanhar o resultado.
- **Empates no teto.** O déficit satura em 100, gerando empates exatos
  (37 municípios em 100,00; 108 em 90 ou mais). A coluna `POSICAO_RANKING`
  desempata por população decrescente, mas isso é critério de listagem, não
  diferença de mérito entre empatados.
- **Pesos iguais.** UBS e leitos SUS entram com peso 50/50 no índice, o que é
  uma escolha arbitrária: uma unidade básica e um leito hospitalar não são
  equivalentes em custo nem em impacto.
- **Índice de oferta, não de necessidade.** O IPIS mede disponibilidade de
  infraestrutura per capita. Não incorpora nenhum indicador de demanda (perfil
  etário, mortalidade evitável, renda, morbidade), embora o nome sugira uma
  medida de prioridade.
- **Competência única.** Apenas a competência mais recente da base de leitos é
  utilizada; 17 municípios presentes em meses anteriores estão ausentes nela,
  o que torna o índice sensível a ruído mensal de cadastro.
- **Código IBGE truncado.** A chave usada tem 6 dígitos, sem o dígito
  verificador, para compatibilidade com as bases do CNES. O
  `resultado_ipis.csv` exporta esse código de 6 dígitos, que **não** é o código
  IBGE oficial de 7 dígitos.

## Estrutura do projeto

```text
CHALLENGE_PRIORISUS/
│
├── RAW/
├── 01_exploracao_ibge.py
├── 02_exploracao_ubs.py
├── 03_integracao_dados.py
├── 04_exploracao_leitos.py
└── 05_integracao_indicadores.py
