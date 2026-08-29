# PrioriSUS

Projeto acadêmico desenvolvido para a Global Solution com foco na análise
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

## Estrutura do projeto

```text
GLOBAL_SOLUTION_PRIORISUS/
│
├── RAW/
├── 01_exploracao_ibge.py
├── 02_exploracao_ubs.py
├── 03_integracao_dados.py
├── 04_exploracao_leitos.py
└── 05_integracao_indicadores.py
