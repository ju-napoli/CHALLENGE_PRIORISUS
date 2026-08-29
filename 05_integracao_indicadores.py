# %%
# 5. Integração dos indicadores

import pandas as pd

# %%
# Carregamos a base municipal do IBGE.

populacao = pd.read_excel(
    "RAW/POP2025_20260113.xls",
    sheet_name="Municípios",
    header=1
)

populacao = populacao[
    populacao["POPULAÇÃO ESTIMADA"].notna()
]

populacao = populacao.drop(columns=["Unnamed: 5"])

populacao["IBGE"] = (
    populacao["COD. UF"].astype(str)
    + populacao["COD. MUNIC"].astype(int).astype(str).str.zfill(5)
).str[:6]

populacao["IBGE"] = populacao["IBGE"].astype("string")

# %%
# Visualizamos a estrutura da base municipal que será utilizada
# como base principal da integração.

populacao[
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA", "IBGE"]
].head()

# %%
# Carregamos a base de UBS.

ubs = pd.read_csv(
    "RAW/Unidades_Basicas_Saude-UBS.csv",
    sep=";"
)

# %%
# Agregamos a quantidade de UBS por município.

ubs_por_municipio = (
    ubs.groupby("IBGE")
    .size()
    .reset_index(name="QTD_UBS")
)

ubs_por_municipio["IBGE"] = (
    ubs_por_municipio["IBGE"].astype("string")
)

ubs_por_municipio.head()

# %%
# Integramos a quantidade de UBS à base municipal do IBGE.

municipios = populacao.merge(
    ubs_por_municipio,
    on="IBGE",
    how="left"
)

municipios.head()

# %%
# Verificamos quantos municípios não possuem registro de UBS.

municipios["QTD_UBS"].isna().sum()

# %%
# Calculamos a quantidade de UBS por 10 mil habitantes.

municipios["UBS_POR_10MIL"] = (
    municipios["QTD_UBS"]
    / municipios["POPULAÇÃO ESTIMADA"]
    * 10000
)

municipios.head()

# %%
# Verificamos quantos municípios possuem valor ausente
# no indicador de UBS por 10 mil habitantes.

municipios["UBS_POR_10MIL"].isna().sum()

# %%
# Carregamos a base de leitos hospitalares.

leitos = pd.read_csv(
    "RAW/Leitos_2026.csv",
    sep=";",
    encoding="latin1"
)

# %%
# Mantemos apenas a competência mais recente disponível.

leitos_julho = leitos[
    leitos["COMP"] == leitos["COMP"].max()
]

leitos_julho.shape

# %%
# Agregamos a quantidade de leitos SUS por município.

leitos_sus_por_municipio = (
    leitos_julho.groupby("CO_IBGE")["LEITOS_SUS"]
    .sum()
    .reset_index(name="QTD_LEITOS_SUS")
)

leitos_sus_por_municipio["CO_IBGE"] = (
    leitos_sus_por_municipio["CO_IBGE"].astype("string")
)

leitos_sus_por_municipio.head()

# %%
# Padronizamos o código IBGE como texto nas duas bases.

municipios["IBGE"] = municipios["IBGE"].astype("string")

leitos_sus_por_municipio["CO_IBGE"] = (
    leitos_sus_por_municipio["CO_IBGE"].astype("string")
)

# %%
# Integramos a quantidade de leitos SUS à base municipal.

municipios = municipios.merge(
    leitos_sus_por_municipio,
    left_on="IBGE",
    right_on="CO_IBGE",
    how="left"
).drop(columns=["CO_IBGE"])

municipios.head()

# %%
# Verificamos quantos municípios não possuem registro de leitos SUS.

municipios["QTD_LEITOS_SUS"].isna().sum()

# %%
# Verificamos quantos municípios possuem registro de leitos SUS.

municipios["QTD_LEITOS_SUS"].notna().sum()

# %%
# Identificamos alguns municípios sem registro de leitos
# para investigar a ausência de correspondência.

municipios[
    municipios["QTD_LEITOS_SUS"].isna()
][
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA", "IBGE"]
].head(20)

# %%
# Calculamos a quantidade de leitos SUS por 10 mil habitantes
# para os municípios com registro na base de leitos.

municipios["LEITOS_SUS_POR_10MIL"] = (
    municipios["QTD_LEITOS_SUS"]
    / municipios["POPULAÇÃO ESTIMADA"]
    * 10000
)

municipios.head()

# %%
# Analisamos a distribuição de leitos SUS por 10 mil habitantes.

municipios["LEITOS_SUS_POR_10MIL"].describe()

# %%
# Resumimos a disponibilidade dos indicadores na base municipal.

municipios[
    ["UBS_POR_10MIL", "LEITOS_SUS_POR_10MIL"]
].notna().sum()

# %%
# Verificamos quantos municípios possuem os dois indicadores disponíveis.

municipios[
    ["UBS_POR_10MIL", "LEITOS_SUS_POR_10MIL"]
].notna().all(axis=1).sum()

# %%
# Selecionamos os municípios com os dois indicadores disponíveis
# para o cálculo do IPIS.

ipis = municipios[
    municipios["UBS_POR_10MIL"].notna()
    & municipios["LEITOS_SUS_POR_10MIL"].notna()
].copy()

ipis.shape

# %%
# Verificamos se não existem valores ausentes nos indicadores
# utilizados no cálculo do IPIS.

ipis[
    ["UBS_POR_10MIL", "LEITOS_SUS_POR_10MIL"]
].isna().sum()

# %%
# Comparamos a distribuição dos dois indicadores que compõem o IPIS.

ipis[
    ["UBS_POR_10MIL", "LEITOS_SUS_POR_10MIL"]
].describe()

# %%
# Verificamos o percentil 95 dos dois indicadores.

ipis[
    ["UBS_POR_10MIL", "LEITOS_SUS_POR_10MIL"]
].quantile(0.95)

# %%
# Normalizamos os indicadores para uma escala de 0 a 100.
# Valores acima do percentil 95 recebem score máximo de 100.

p95_ubs = ipis["UBS_POR_10MIL"].quantile(0.95)
p95_leitos = ipis["LEITOS_SUS_POR_10MIL"].quantile(0.95)

ipis["SCORE_UBS"] = (
    ipis["UBS_POR_10MIL"] / p95_ubs * 100
).clip(upper=100)

ipis["SCORE_LEITOS"] = (
    ipis["LEITOS_SUS_POR_10MIL"] / p95_leitos * 100
).clip(upper=100)

ipis.head()

# %%
# Invertemos os scores de infraestrutura para representar deficiência de infraestrutura.
# Quanto menor a disponibilidade de UBS ou leitos, maior será o déficit e, consequentemente,
# maior será a prioridade de investimento.

ipis["DEFICIT_UBS"] = 100 - ipis["SCORE_UBS"]

ipis["DEFICIT_LEITOS"] = 100 - ipis["SCORE_LEITOS"]

ipis[
    [
        "SCORE_UBS",
        "DEFICIT_UBS",
        "SCORE_LEITOS",
        "DEFICIT_LEITOS"
    ]
].head()
# %%
# Calculamos o IPIS como a média dos déficits de UBS e leitos SUS.
#
# Quanto maior o IPIS, maior a deficiência de infraestrutura
# e maior a prioridade de investimento em saúde.

ipis["IPIS"] = (
    ipis["DEFICIT_UBS"]
    + ipis["DEFICIT_LEITOS"]
) / 2

ipis.head()

# %%
# Analisamos a distribuição do IPIS.

ipis["IPIS"].describe()

# %%
# Identificamos os municípios com maiores valores de IPIS (maior prioridade de investimento).

ipis.nlargest(
    10,
    "IPIS"
)[
    [
        "UF",
        "NOME DO MUNICÍPIO",
        "POPULAÇÃO ESTIMADA",
        "UBS_POR_10MIL",
        "LEITOS_SUS_POR_10MIL",
        "SCORE_UBS",
        "SCORE_LEITOS",
        "IPIS"
    ]
]

# %%
# Identificamos os municípios com menores valores de IPIS (menor prioridade de investimento).

ipis.nsmallest(
    10,
    "IPIS"
)[
    [
        "UF",
        "NOME DO MUNICÍPIO",
        "POPULAÇÃO ESTIMADA",
        "UBS_POR_10MIL",
        "LEITOS_SUS_POR_10MIL",
        "SCORE_UBS",
        "SCORE_LEITOS",
        "IPIS"
    ]
]

# %%
# Identificamos os municípios com menores valores de IPIS.

ipis.nsmallest(
    10,
    "IPIS"
)[
    [
        "UF",
        "NOME DO MUNICÍPIO",
        "POPULAÇÃO ESTIMADA",
        "UBS_POR_10MIL",
        "LEITOS_SUS_POR_10MIL",
        "SCORE_UBS",
        "SCORE_LEITOS",
        "IPIS"
    ]
]

# %%
# Criamos faixas para analisar a distribuição do IPIS.

ipis["FAIXA_IPIS"] = pd.cut(
    ipis["IPIS"],
    bins=[0, 30, 70, 100],
    labels=[
        "Baixa prioridade",
        "Prioridade moderada",
        "Alta prioridade"
    ],
    include_lowest=True
)

ipis["FAIXA_IPIS"].value_counts().sort_index()

# %%
