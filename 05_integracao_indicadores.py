# %%
# 5. Integração dos indicadores

from pathlib import Path

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
# Validamos a base municipal antes de qualquer integração.
#
# A chave IBGE é montada concatenando COD. UF com COD. MUNIC. Se uma versão
# futura do arquivo fizer o pandas inferir COD. UF como float, astype(str)
# produziria "11.0" em vez de "11" e todas as chaves quebrariam em silêncio:
# os merges continuariam rodando e devolveriam 100% de NaN, sem erro.
# As asserções abaixo transformam essa falha silenciosa em falha imediata.

assert len(populacao) == 5571, (
    f"Esperados 5.571 municípios na base do IBGE, encontrados {len(populacao)}."
)

assert populacao["IBGE"].str.len().eq(6).all(), (
    "Há chaves IBGE que não possuem 6 caracteres."
)

assert not populacao["IBGE"].duplicated().any(), (
    "Há chaves IBGE duplicadas na base municipal."
)

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
# Sinalizamos a ausência de dado de UBS em vez de preenchê-la com zero.
#
# Decisão assimétrica em relação aos leitos (ver adiante): a ausência de um
# município na base de UBS é provável lacuna de cadastro, e não informação
# confiável de que o município não possua nenhuma unidade básica.
#
# Evidência da auditoria: dos 83 municípios sem correspondência na base de
# UBS, 46 possuem hospital com leitos SUS registrados no CNES. O maior deles,
# Araruama/RJ, tem 137.906 habitantes, 4 estabelecimentos hospitalares e
# 186 leitos SUS — é implausível que não tenha nenhuma UBS.
#
# Preencher com zero daria déficit máximo (e prioridade máxima de
# investimento) a municípios cujo problema é o registro, não a infraestrutura.
# Por isso mantemos QTD_UBS e UBS_POR_10MIL como NaN e marcamos a linha.

municipios["DADO_UBS_AUSENTE"] = municipios["QTD_UBS"].isna()

municipios["DADO_UBS_AUSENTE"].sum()

# %%
# Calculamos a quantidade de UBS por 10 mil habitantes.
# Municípios com DADO_UBS_AUSENTE = True permanecem com NaN neste indicador.

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
# Tratamos a ausência de registro de leitos como zero leitos, não como
# dado desconhecido.
#
# Justificativa: a base de leitos é um cadastro de estabelecimentos que
# POSSUEM leitos. Nenhuma das linhas da competência mais recente tem
# LEITOS_EXISTENTES == 0, e todos os DS_TIPO_UNIDADE são hospitais, unidades
# mistas ou prontos-socorros. Um município ausente da base não é um município
# cujo número de leitos é desconhecido — é um município que não possui
# nenhum estabelecimento com leito. A ausência aqui É um zero.
#
# Manter esses municípios como NaN produzia uma contradição no índice:
# municípios com zero leitos SUS explicitamente registrado recebiam déficit
# máximo e iam ao topo do ranking, enquanto municípios na mesma situação de
# fato, porém ausentes da base, eram descartados do ranking inteiro.

municipios["QTD_LEITOS_SUS"] = municipios["QTD_LEITOS_SUS"].fillna(0)

municipios["QTD_LEITOS_SUS"].isna().sum()

# %%
# Calculamos a quantidade de leitos SUS por 10 mil habitantes.
# Após o fillna(0) acima, todos os municípios possuem este indicador.

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
# Todos os municípios da base do IBGE seguem para o cálculo do IPIS.
#
# A versão anterior filtrava aqui com .notna() nos dois indicadores e
# descartava 2.059 municípios (36,96% do país, 15,4 milhões de habitantes).
# O filtro contradizia o propósito do índice: os municípios sem nenhuma das
# duas infraestruturas — os de maior prioridade de investimento — eram
# justamente os eliminados do ranking.
#
# O filtro deixa de ser necessário porque a ausência de leitos passou a ser
# tratada como zero, e a ausência de UBS passou a ser tratada como componente
# indisponível (a linha permanece, ver o cálculo do IPIS adiante).

ipis = municipios.copy()

assert len(ipis) == 5571, (
    f"Esperados 5.571 municípios no cálculo do IPIS, encontrados {len(ipis)}."
)

ipis.shape

# %%
# Verificamos os valores ausentes remanescentes nos indicadores.
# Espera-se NaN apenas em UBS_POR_10MIL, nos municípios marcados com
# DADO_UBS_AUSENTE, e nenhum NaN em LEITOS_SUS_POR_10MIL.

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
#
# Os percentis são calculados sobre a base completa de 5.571 municípios.
# Na versão anterior eles eram calculados sobre a amostra já filtrada de
# 3.512 municípios, o que contaminava até o score de quem permanecia no
# ranking: como SCORE = valor / p95 * 100, uma régua calibrada sobre uma
# amostra enviesada reordenava o ranking inteiro.
#
# Para UBS_POR_10MIL o quantile ignora os NaN dos municípios marcados com
# DADO_UBS_AUSENTE, ou seja, a régua é calibrada sobre os municípios que
# de fato possuem dado de UBS — sem tratar dado ausente como zero.

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
# Calculamos o IPIS como a média dos déficits disponíveis.
#
# Quanto maior o IPIS, maior a deficiência de infraestrutura
# e maior a prioridade de investimento em saúde.
#
# Usamos .mean(axis=1), que ignora NaN, em vez da soma dividida por 2.
# Para os municípios marcados com DADO_UBS_AUSENTE o IPIS passa a ser
# calculado apenas sobre DEFICIT_LEITOS: eles permanecem no ranking, mas
# nenhum valor é inventado para o componente de UBS que não temos.
#
# A coluna DADO_UBS_AUSENTE acompanha o resultado final justamente para que
# o leitor saiba quais posições do ranking se apoiam em um único componente.

ipis["IPIS"] = ipis[
    ["DEFICIT_UBS", "DEFICIT_LEITOS"]
].mean(axis=1)

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
# Criamos faixas para analisar a distribuição do IPIS.

# As faixas são definidas pelos tercis da distribuição observada, e não por
# cortes fixos.
#
# A versão anterior usava bins fixos [0, 30, 70, 100], calibrados para a
# distribuição da amostra filtrada de 3.512 municípios. Aplicados à base
# completa, esses cortes concentravam 61% dos municípios em uma única faixa
# ("Prioridade moderada") e classificavam 32% como "Alta prioridade" — uma
# faixa com um terço do país perde o poder de discriminação necessário para
# orientar alocação de orçamento.
#
# Os tercis dividem os 5.571 municípios em três grupos de tamanho equivalente
# (~1.857 cada), de modo que "Alta prioridade" passe a significar
# "no terço mais carente do país" — uma afirmação relativa, verificável e
# diretamente utilizável para priorização orçamentária.
#
# Consequência a ter em mente: por serem relativos, os cortes se deslocam
# quando a base é atualizada. Os valores efetivamente usados ficam registrados
# em q33_ipis e q67_ipis e devem ser reportados junto com o resultado.

q33_ipis = ipis["IPIS"].quantile(1 / 3)
q67_ipis = ipis["IPIS"].quantile(2 / 3)

ipis["FAIXA_IPIS"] = pd.cut(
    ipis["IPIS"],
    bins=[0, q33_ipis, q67_ipis, 100],
    labels=[
        "Baixa prioridade",
        "Prioridade moderada",
        "Alta prioridade"
    ],
    include_lowest=True
)

print(f"Cortes das faixas (tercis): q33 = {q33_ipis:.4f} | q67 = {q67_ipis:.4f}")

ipis["FAIXA_IPIS"].value_counts().sort_index()


# %%
# Ordenamos o resultado e materializamos a posição no ranking.
#
# O IPIS satura em 100 por construção (o déficit é limitado a esse teto), o
# que produz empates exatos: 37 municípios com IPIS = 100,00 e 108 com
# IPIS >= 90. Sem critério de desempate, a ordem entre eles no CSV seria
# arbitrária — definida pela ordem de leitura do arquivo do IBGE.
#
# Desempatamos por POPULAÇÃO ESTIMADA em ordem decrescente: entre dois
# municípios com o mesmo déficit de infraestrutura, o de maior população
# afeta mais pessoas e é listado primeiro.
#
# Este critério afeta APENAS a ordenação e a coluna POSICAO_RANKING.
# O valor de IPIS não é alterado — municípios empatados continuam com o
# mesmo IPIS, e a coluna POSICAO_RANKING deve ser lida como ordem de
# listagem, não como diferença de mérito entre empatados.

ipis = ipis.sort_values(
    ["IPIS", "POPULAÇÃO ESTIMADA"],
    ascending=[False, False]
)

ipis["POSICAO_RANKING"] = range(1, len(ipis) + 1)

colunas_saida = [
    "POSICAO_RANKING",
    "IBGE",
    "UF",
    "NOME DO MUNICÍPIO",
    "POPULAÇÃO ESTIMADA",
    "QTD_UBS",
    "UBS_POR_10MIL",
    "DADO_UBS_AUSENTE",
    "QTD_LEITOS_SUS",
    "LEITOS_SUS_POR_10MIL",
    "DEFICIT_UBS",
    "DEFICIT_LEITOS",
    "IPIS",
    "FAIXA_IPIS"
]

resultado_ipis = ipis[colunas_saida]

# Gravamos o resultado em OUTPUT/, que é o caminho lido pelo script 06.
# A pasta é criada caso ainda não exista.

pasta_output = Path("OUTPUT")
pasta_output.mkdir(
    parents=True,
    exist_ok=True
)

resultado_ipis.to_csv(
    pasta_output / "resultado_ipis.csv",
    index=False,
    encoding="utf-8-sig"
)

print(resultado_ipis.head(10))# %%
