# %%
# 3. Integração das bases de dados

import pandas as pd


# %%
# Carregamos a base de população do IBGE.

populacao = pd.read_excel(
    "RAW/POP2025_20260113.xls",
    sheet_name="Municípios",
    header=1
)

populacao = populacao[
    populacao["POPULAÇÃO ESTIMADA"].notna()
]

populacao = populacao.drop(columns=["Unnamed: 5"])


# %%
# Criamos o código IBGE no mesmo padrão utilizado pela base de UBS.

populacao["IBGE"] = (
    populacao["COD. UF"].astype(str)
    + populacao["COD. MUNIC"].astype(int).astype(str).str.zfill(5)
).str[:6]


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


# %%
# Padronizamos a chave IBGE como texto nas duas bases.

populacao["IBGE"] = populacao["IBGE"].astype("string")
ubs_por_municipio["IBGE"] = ubs_por_municipio["IBGE"].astype("string")


# %%
# Integramos a quantidade de UBS à base de população.
# Mantemos todos os municípios presentes na base do IBGE.

municipios = populacao.merge(
    ubs_por_municipio,
    on="IBGE",
    how="left"
)

municipios.head()


# %%
# Verificamos quantos municípios encontraram correspondência na base de UBS.

municipios["QTD_UBS"].notna().sum()


# %%
# Verificamos quantos municípios não encontraram correspondência.

municipios["QTD_UBS"].isna().sum()


# %%
# Identificamos os municípios que não possuem correspondência na base de UBS.

municipios[municipios["QTD_UBS"].isna()][
    ["UF", "NOME DO MUNICÍPIO", "IBGE"]
].head(20)


# %%
# Verificamos quais municípios da base de UBS não encontraram
# correspondência na base de população.

ubs_por_municipio[
    ~ubs_por_municipio["IBGE"].isin(municipios["IBGE"])
].sort_values("IBGE")


# %%
# Identificamos o município correspondente ao código 530040 na base de UBS.

ubs[ubs["IBGE"] == 530040][
    ["UF", "IBGE", "NOME"]
]

# Observação:
# A base de UBS possui um registro com IBGE = 530040 (CSC 01 Ceilândia),
# que não possui correspondência na base municipal do IBGE.
# Mantemos o registro fora da integração por não haver correspondência
# direta entre as chaves das fontes.

# %%
# Analisamos a população dos municípios sem correspondência na base de UBS.

municipios_sem_ubs = municipios[
    municipios["QTD_UBS"].isna()
]

municipios_sem_ubs["POPULAÇÃO ESTIMADA"].describe()

# %%
# Visualizamos os municípios sem correspondência e suas populações.

municipios_sem_ubs[
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA", "IBGE"]
].sort_values(
    "POPULAÇÃO ESTIMADA",
    ascending=False
).head(20)

# %%
# Verificamos a distribuição dos municípios sem correspondência por estado.

municipios_sem_ubs["UF"].value_counts().sort_index()
# %%
# Procuramos Araruama diretamente pelo nome na base de UBS.

ubs[
    ubs["NOME"].str.contains(
        "Araruama",
        case=False,
        na=False
    )
][
    ["UF", "IBGE", "NOME"]
]

# %%
# Calculamos a cobertura da base de UBS em relação aos municípios do IBGE.

cobertura_ubs = (
    municipios["QTD_UBS"].notna().mean() * 100
)

cobertura_ubs

# %%
# Calculamos a quantidade de UBS por 10 mil habitantes.
# O cálculo será realizado apenas para os municípios
# com correspondência na base de UBS.

municipios["UBS_POR_10MIL"] = (
    municipios["QTD_UBS"]
    / municipios["POPULAÇÃO ESTIMADA"]
    * 10000
)

# %%
# Visualizamos a nova variável.

municipios[
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA",
     "QTD_UBS", "UBS_POR_10MIL"]
].head(10)

# %%
# Identificamos os municípios com maiores valores de UBS por 10 mil habitantes.

municipios.nlargest(
    10,
    "UBS_POR_10MIL"
)[
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA",
     "QTD_UBS", "UBS_POR_10MIL"]
]

# %%
municipios["UBS_POR_10MIL"].describe()

# %%
# A variável UBS_POR_10MIL apresenta assimetria,
# com valores elevados principalmente em municípios de pequena população.
# Por isso, valores extremos deverão ser avaliados antes da normalização
# e incorporação ao indicador final.