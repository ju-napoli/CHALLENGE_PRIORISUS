# %%
# 4. Exploração dos dados de leitos

import pandas as pd

# %%
# Carregamos a população municipal do IBGE para análises comparativas.

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
# Carregamos a base de leitos hospitalares.
# O arquivo utiliza ponto e vírgula como separador
# e codificação latin1.

leitos = pd.read_csv(
    "RAW/Leitos_2026.csv",
    sep=";",
    encoding="latin1"
)

leitos.head()
# %%
# Verificamos a quantidade de registros e colunas disponíveis.

leitos.shape

# %%
# Verificamos os nomes das colunas disponíveis.

leitos.columns

# %%
# Verificamos os tipos de dados das colunas.

leitos.dtypes

# %%
# Verificamos a quantidade de valores ausentes em cada coluna.

leitos.isna().sum()

# %%
# Verificamos os valores ausentes nas variáveis relacionadas aos leitos.

leitos[
    [
        "CO_IBGE",
        "MUNICIPIO",
        "LEITOS_EXISTENTES",
        "LEITOS_SUS"
    ]
].isna().sum()

# %%
# Verificamos se cada estabelecimento possui um código CNES único.

leitos["CNES"].nunique()
# %%
# Verificamos a quantidade total de registros da base.

len(leitos)

# %%
# Verificamos se existem registros duplicados considerando
# estabelecimento e município.

leitos.duplicated(
    subset=["CNES", "CO_IBGE"]
).sum()

# %%
# Investigamos por que um mesmo estabelecimento aparece em várias linhas.

leitos[leitos["CNES"] == leitos["CNES"].iloc[0]][
    [
        "COMP",
        "CO_IBGE",
        "MUNICIPIO",
        "CNES",
        "NOME_ESTABELECIMENTO",
        "LEITOS_EXISTENTES",
        "LEITOS_SUS"
    ]
]

# %%
# Verificamos as competências disponíveis na base.

leitos["COMP"].unique()

# %%
# Verificamos a competência mais recente disponível.

leitos["COMP"].max()
# %%
# Mantemos apenas a competência mais recente disponível na base.

leitos_julho = leitos[
    leitos["COMP"] == leitos["COMP"].max()
]

leitos_julho.shape

# %%
# Verificamos a quantidade de estabelecimentos registrados
# na competência mais recente.

leitos_julho["CNES"].nunique()

# %%
# Verificamos se ainda existem registros duplicados
# para o mesmo estabelecimento e município.

leitos_julho.duplicated(
    subset=["CNES", "CO_IBGE"]
).sum()

# %%
# Agregamos a quantidade de leitos por município.
# Cada município recebe a soma dos leitos de seus estabelecimentos
# na competência mais recente disponível.

leitos_por_municipio = (
    leitos_julho.groupby("CO_IBGE")["LEITOS_EXISTENTES"]
    .sum()
    .reset_index(name="QTD_LEITOS")
)

leitos_por_municipio.head()

# %%
# Verificamos quantos municípios possuem registros de leitos.

leitos_por_municipio.shape

# %%
# Identificamos os municípios com maior quantidade de leitos.

leitos_por_municipio.nlargest(
    10,
    "QTD_LEITOS"
)

# %%
# Verificamos a cobertura da base de leitos em relação aos municípios do IBGE.

cobertura_leitos = (
    leitos_por_municipio["CO_IBGE"].nunique()
    / populacao["IBGE"].nunique()
    * 100
)

cobertura_leitos

# %%
# Padronizamos o código IBGE da base de leitos como texto.

leitos_por_municipio["CO_IBGE"] = (
    leitos_por_municipio["CO_IBGE"]
    .astype(str)
)

# %%
# Verificamos quantos municípios da base do IBGE não possuem
# correspondência na base de leitos.

municipios_sem_leitos = populacao[
    ~populacao["IBGE"].isin(leitos_por_municipio["CO_IBGE"])
]

municipios_sem_leitos[
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA", "IBGE"]
].head(20)

# %%
# Verificamos a quantidade de municípios sem correspondência.

municipios_sem_leitos.shape

# %%
# Analisamos a distribuição da quantidade de leitos por município.

leitos_por_municipio["QTD_LEITOS"].describe()


# %%
# Adicionamos a população estimada à base agregada de leitos.

leitos_por_municipio = leitos_por_municipio.merge(
    populacao[["IBGE", "POPULAÇÃO ESTIMADA"]],
    left_on="CO_IBGE",
    right_on="IBGE",
    how="left"
).drop(columns=["IBGE"])

leitos_por_municipio.head()


# %%
# Calculamos a quantidade de leitos por 10 mil habitantes.
# Utilizamos a população estimada do IBGE como denominador.

leitos_por_municipio["LEITOS_POR_10MIL"] = (
    leitos_por_municipio["QTD_LEITOS"]
    / leitos_por_municipio["POPULAÇÃO ESTIMADA"]
    * 10000
)

leitos_por_municipio.head()


# %%
# Analisamos a distribuição de leitos por 10 mil habitantes.

leitos_por_municipio["LEITOS_POR_10MIL"].describe()


# %%
# Identificamos os municípios com maiores valores de leitos
# por 10 mil habitantes.

leitos_por_municipio.nlargest(
    10,
    "LEITOS_POR_10MIL"
)[
    ["CO_IBGE", "QTD_LEITOS", "POPULAÇÃO ESTIMADA", "LEITOS_POR_10MIL"]
]
# %%
# Comparamos a quantidade total de leitos com a quantidade de leitos SUS.

leitos_julho[
    ["LEITOS_EXISTENTES", "LEITOS_SUS"]
].describe()

# %%
# Verificamos a proporção de leitos SUS em relação ao total de leitos.

proporcao_sus = (
    leitos_julho["LEITOS_SUS"]
    / leitos_julho["LEITOS_EXISTENTES"]
)

proporcao_sus.describe()

# %%
# Agregamos a quantidade de leitos SUS por município.

leitos_sus_por_municipio = (
    leitos_julho.groupby("CO_IBGE")["LEITOS_SUS"]
    .sum()
    .reset_index(name="QTD_LEITOS_SUS")
)

leitos_sus_por_municipio.head()

# %%
# Padronizamos o código IBGE como texto nas duas bases.

leitos_por_municipio["CO_IBGE"] = (
    leitos_por_municipio["CO_IBGE"].astype("string")
)

leitos_sus_por_municipio["CO_IBGE"] = (
    leitos_sus_por_municipio["CO_IBGE"].astype("string")
)

# %%
# Adicionamos a quantidade de leitos SUS à base agregada de leitos.

leitos_por_municipio = leitos_por_municipio.merge(
    leitos_sus_por_municipio,
    on="CO_IBGE",
    how="left"
)

leitos_por_municipio.head()

# %%
# Calculamos a quantidade de leitos SUS por 10 mil habitantes.

leitos_por_municipio["LEITOS_SUS_POR_10MIL"] = (
    leitos_por_municipio["QTD_LEITOS_SUS"]
    / leitos_por_municipio["POPULAÇÃO ESTIMADA"]
    * 10000
)

leitos_por_municipio.head()

# %%
# Analisamos a distribuição de leitos SUS por 10 mil habitantes.

leitos_por_municipio["LEITOS_SUS_POR_10MIL"].describe()

# %%
# Identificamos os municípios com maiores valores de leitos SUS
# por 10 mil habitantes.

leitos_por_municipio.nlargest(
    10,
    "LEITOS_SUS_POR_10MIL"
)[
    ["CO_IBGE", "QTD_LEITOS_SUS", "POPULAÇÃO ESTIMADA", "LEITOS_SUS_POR_10MIL"]
]

# %%
# Verificamos quantos municípios possuem registro de leitos,
# mas nenhum leito SUS.

(leitos_por_municipio["QTD_LEITOS_SUS"] == 0).sum()

# %%
# Verificamos quantos municípios possuem algum leito SUS.

(leitos_por_municipio["QTD_LEITOS_SUS"] > 0).sum()

# %%
