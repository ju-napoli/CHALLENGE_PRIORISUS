# Diagnóstico do pipeline PrioriSUS

**Data da auditoria:** 2026-08-31
**Escopo:** scripts `01` a `06`, rastreando perda de linhas/municípios em cada merge e cada filtro.
**Método:** script auxiliar de auditoria que reexecuta a lógica exata dos scripts 03/04/05 com instrumentação em cada etapa. O resultado recalculado bate **exatamente** com o `OUTPUT/resultado_ipis.csv` já existente (3.512 linhas, mesmos códigos IBGE), então todos os números abaixo descrevem o pipeline como ele roda hoje.

> **Nota de ambiente:** o pipeline **não roda out-of-the-box**. `pd.read_excel` sobre o `.xls` legado (formato OLE2) exige o pacote `xlrd`, que não estava instalado. Foi necessário instalar `xlrd 2.0.2` para executar 01/03/04/05. Ver seção 5(c).

---

## 1. Rastreamento de linhas por etapa

### 1.1 Visão geral (funil)

| # | Etapa | Script:linha | Entram | Saem | Perda |
|---|-------|--------------|-------:|-----:|------:|
| A | Leitura aba `Municípios` do IBGE | `03:10-14` / `05:9-13` | — | 5.602 | — |
| B | Filtro `POPULAÇÃO ESTIMADA.notna()` | `03:16-18` / `05:15-17` | 5.602 | **5.571** | −31 |
| C | Merge 1 — LEFT JOIN UBS | `03:62-66` / `05:62-66` | 5.571 | 5.571 | 0 linhas (**83 sem match**) |
| D | Filtro competência `COMP == max` | `04:116-118` / `05:104-106` | 50.388 | 7.208 | −43.180 linhas |
| E | Merge 2 — LEFT JOIN leitos SUS | `05:137-142` | 5.571 | 5.571 | 0 linhas (**2.013 sem match**) |
| F | **Filtro final `notna & notna`** | **`05:201-204`** | 5.571 | **3.512** | **−2.059 municípios** |

O funil de linhas nunca perde registros nos merges (todos são `how="left"` sobre a base do IBGE). **Toda a perda de municípios acontece em um único ponto: o filtro da etapa F.**

---

### 1.2 Etapa B — filtro `.notna()` na população (5.602 → 5.571)

- **Entram:** 5.602 linhas da aba `Municípios`
- **Saem:** 5.571
- **Perdidas:** 31 linhas

**Motivo — benigno e correto.** As 31 linhas não são municípios: são o rodapé do arquivo do IBGE (linha em branco, `Fonte: IBGE. Diretoria de Pesquisas...`, `Notas:` e 27 notas de rodapé sobre populações judiciais de municípios do AM). O filtro faz exatamente o que deveria.

Verificações da chave após esta etapa:
- Chave `IBGE` gerada: 5.571 valores, **todos com 6 caracteres**, **0 duplicados**
- População total coberta: **213.421.037** habitantes
- Tipos de origem: `COD. UF` = `object`, `COD. MUNIC` = `float64`

⚠️ **Fragilidade silenciosa (não é bug hoje, mas é uma bomba-relógio):** a chave é montada com `populacao["COD. UF"].astype(str)` (`03:26-29`, `05:21-24`). Hoje `COD. UF` vem como `object` contendo strings (`"11"`, `"35"`), então funciona. Se uma versão futura do arquivo fizer o pandas inferir `float64` nessa coluna, `astype(str)` produzirá `"11.0"` e **todas as chaves quebram silenciosamente** — o merge continuaria rodando e retornando 100% de NaN, sem erro. Não há nenhuma asserção protegendo isso.

---

### 1.3 Base UBS e Merge 1 (perda: 83 municípios)

**Base UBS (`RAW/Unidades_Basicas_Saude-UBS.csv`):**
- 47.913 unidades (linhas)
- Coluna `IBGE`: `int64`, 0 nulos, **todos com 6 dígitos** → chave compatível
- Após `groupby("IBGE").size()` → **5.489 municípios distintos**

**Merge 1 (`03:62-66`, `05:62-66`):**

```python
municipios = populacao.merge(ubs_por_municipio, on="IBGE", how="left")
```

| Métrica | Valor |
|---|---|
| Entram (esquerda / população) | 5.571 |
| Entram (direita / UBS agregada) | 5.489 |
| **Saem** | **5.571** (nenhuma linha perdida — é LEFT JOIN) |
| Municípios **com** correspondência | 5.488 |
| Municípios **sem** correspondência (`QTD_UBS = NaN`) | **83** |
| Cobertura | **98,51 %** |
| Órfãos do lado direito (UBS sem município) | **1** → código `530040`, "CSC 01 CEILANDIA" (DF) |

**Sobre o órfão `530040`:** o DF tem um único município na base do IBGE (`530010`, Brasília). A base de UBS traz 210 unidades sob `530010` e 1 sob `530040` (região administrativa de Ceilândia, que não é município). É 1 UBS perdida em 47.913 — irrelevante numericamente, mas o comentário em `03:107-111` documenta corretamente a decisão.

**Perfil dos 83 municípios sem UBS:**
- População total: 1.080.157 | mediana: 7.048 | máximo: **137.906** (Araruama/RJ)
- Concentração por UF: **RS 36**, PR 9, SP 6, RJ 4, PA 4, AM 3, MG 3, demais ≤ 2

🔴 **Isso quase certamente é lacuna de cadastro, não ausência real de UBS.** Evidência forte: **46 desses 83 municípios têm hospital com leitos SUS registrados** na base do CNES. Araruama/RJ tem 137.906 habitantes, **4 estabelecimentos hospitalares e 186 leitos SUS** — e zero UBS na base. É implausível que uma cidade desse porte não tenha nenhuma unidade básica.

Confirmação adicional: o próprio script 03 (`03:137-147`) busca "Araruama" pelo nome na base de UBS. O resultado são 2 unidades, mas nenhuma delas é de Araruama — `330510` é *São João de Meriti/RJ* ("UNIDADE DE SAUDE DA FAMILIA PARQUE ARARUAMA") e `522185` é *Valparaíso de Goiás/GO*. Ou seja: a busca por nome **não** resgatou o município; a ausência é da base de origem.

---

### 1.4 Base de leitos e filtro de competência (etapa D)

**Base (`RAW/Leitos_2026.csv`):** 50.388 linhas, 35 colunas.

**Competências disponíveis** — 7 meses de 2026:

| COMP | Linhas |
|---|---:|
| 202601 | 7.212 |
| 202602 | 7.202 |
| 202603 | 7.188 |
| 202604 | 7.181 |
| 202605 | 7.183 |
| 202606 | 7.214 |
| **202607** | **7.208** |

**Filtro `leitos["COMP"] == leitos["COMP"].max()`** (`04:116-118`, `05:104-106`):
- Entram: 50.388 linhas → Saem: **7.208** (descartadas 43.180)
- Municípios distintos em **toda** a base: **3.575**
- Municípios distintos na competência mais recente: **3.558**
- 🟡 **17 municípios existem na base de leitos mas desaparecem ao filtrar só o último mês**

Os 17: Tapauá/AM, Piraquê/TO, Varjota/CE, Jardim de Angicos/RN, São Vicente/RN, Mulungu/PB, Poço Dantas/PB, Boquim/SE, Laranjeiras/SE, Cabaceiras do Paraguaçu/BA, Crucilândia/MG, Carapebus/RJ, Araçoiaba da Serra/SP, Eldorado/SP, Adrianópolis/PR, Pinhão/PR, Bonfinópolis/GO. Vários aparecem em 5 ou 6 das 7 competências e somem exatamente no mês escolhido. **Usar um único mês torna o índice sensível a ruído de cadastro mensal.**

Qualidade da base filtrada:
- `CO_IBGE`: `int64`, **6 dígitos**, 100% com correspondência no IBGE (**0 órfãos**)
- `LEITOS_SUS` e `LEITOS_EXISTENTES`: **0 nulos**
- **0 duplicatas** de `CNES + CO_IBGE`; 7.208 CNES distintos para 7.208 linhas
- `MOTIVO_DESABILITACAO`: 0 preenchidos (nenhum estabelecimento desabilitado)
- Após `groupby("CO_IBGE")` → **3.558 municípios**

🔑 **Fato decisivo para a seção 3:** **nenhum** estabelecimento na base tem `LEITOS_EXISTENTES == 0`, e os tipos de unidade são exclusivamente Hospital Geral (5.554), Hospital Especializado (1.058), Unidade Mista (496), Pronto Socorro Geral (74) e Pronto Socorro Especializado (26). Ou seja: **a base só contém estabelecimentos que têm leitos.** Um município ausente da base não é "dado faltante" — ele não tem nenhum estabelecimento com leito. **Ausência aqui significa zero, não desconhecido.**

---

### 1.5 Merge 2 — leitos SUS (perda: 2.013 municípios)

```python
municipios = municipios.merge(
    leitos_sus_por_municipio, left_on="IBGE", right_on="CO_IBGE", how="left"
).drop(columns=["CO_IBGE"])
```

| Métrica | Valor |
|---|---|
| Entram (esquerda) | 5.571 |
| Entram (direita / leitos agregados) | 3.558 |
| **Saem** | **5.571** (LEFT JOIN, nenhuma linha perdida) |
| Municípios **com** registro de leitos SUS | 3.558 |
| Municípios **sem** registro (`QTD_LEITOS_SUS = NaN`) | **2.013** |
| Cobertura | **63,87 %** |
| Órfãos do lado direito | **0** |

**Perfil dos 2.013 sem leitos:**
- População total: 14.529.820 | mediana: 4.924 | máximo: 125.861 (Almirante Tamandaré/PR)
- Média de 3,3 UBS por município (ou seja: **têm** atenção básica, não têm hospital)
- Concentração por UF: **MG 445**, SP 293, RS 261, PR 162, SC 138, PB 122, PI 102, TO 92, BA 70, SE 54, GO 53, AL 52, MT 49

Os maiores excluídos por falta de leitos incluem **Almirante Tamandaré/PR (125.861 hab, 14 UBS)**, **Jandira/SP (121.550 hab, 10 UBS)** e **Poá/SP (106.355 hab, 17 UBS)**.

🟡 **Distinção importante:** aqui a ausência tem duas leituras possíveis. Para a maioria (mediana ~4.9 mil hab) é o padrão brasileiro real — município pequeno sem hospital, referenciado a um polo regional. Mas para os casos de 100 mil+ habitantes na região metropolitana, é ausência de hospital *no território*, o que é uma informação genuína e relevante para priorização, não um erro de dado.

---

### 1.6 Etapa F — o filtro que descarta municípios

Esta é a **única** etapa que reduz o número de municípios.

| Métrica | Valor |
|---|---|
| Entram | **5.571** |
| Saem | **3.512** |
| **Excluídos** | **2.059 (36,96 %)** |
| População excluída | **15.415.413 hab (7,22 % da população nacional)** |

**Decomposição da exclusão:**

| Motivo | Municípios |
|---|---:|
| Só falta UBS (tem leitos SUS) | **46** |
| Só falta leitos SUS (tem UBS) | **1.976** |
| Faltam os dois | **37** |
| **Total** | **2.059** |

**Perfil populacional dos excluídos:** média 7.487 | mediana 4.989 | mín 856 | máx 137.906 | P75 = 8.576.
São esmagadoramente municípios pequenos.

**Excluídos por UF (top 15):** MG 447 · SP 294 · RS 275 · PR 167 · SC 138 · PB 124 · PI 103 · TO 92 · BA 72 · GO 55 · SE 54 · AL 52 · MT 50 · RN 32 · ES 28.

---

## 2. Quantos municípios não aparecem no `resultado_ipis.csv` e por quê

### Resposta direta

> **2.059 dos 5.571 municípios brasileiros (36,96 %) não aparecem no `resultado_ipis.csv`.**
> O arquivo final tem **3.512 linhas** — confirmado tanto no CSV existente quanto no recálculo.
> Isso equivale a **15.415.413 habitantes (7,22 % da população do país)** fora do ranking de prioridade.

### A linha de código responsável

**`05_integracao_indicadores.py`, linhas 201-204:**

```python
ipis = municipios[
    municipios["UBS_POR_10MIL"].notna()
    & municipios["LEITOS_SUS_POR_10MIL"].notna()
].copy()
```

Essa é a **única** instrução do pipeline que remove municípios. Todo o resto (`05:62-66` e `05:137-142`) usa `how="left"` e preserva as 5.571 linhas.

### A cadeia causal exata

O `NaN` que o filtro rejeita nasce em duas etapas anteriores:

1. **`05:62-66`** — LEFT JOIN com UBS deixa `QTD_UBS = NaN` para 83 municípios sem registro de UBS.
2. **`05:78-82`** — `UBS_POR_10MIL = QTD_UBS / POPULAÇÃO * 10000` propaga o `NaN` (NaN em qualquer operação aritmética continua NaN).
3. **`05:137-142`** — LEFT JOIN com leitos deixa `QTD_LEITOS_SUS = NaN` para 2.013 municípios.
4. **`05:170-174`** — `LEITOS_SUS_POR_10MIL` propaga esse `NaN`.
5. **`05:201-204`** — o filtro `notna & notna` descarta as 2.059 linhas afetadas por (2) ou (4).

**Em uma frase:** *"ausência de registro na base de origem"* é convertida em `NaN` pelo LEFT JOIN, propagada pela divisão, e finalmente reinterpretada pelo filtro como *"município inelegível para o ranking"* — três significados diferentes colapsados na mesma representação, sem nenhuma decisão explícita em nenhum ponto.

---

## 3. Avaliação crítica: descartar faz sentido para um índice de PRIORIDADE?

**Resposta curta: não. É o defeito metodológico mais grave do projeto, e ele inverte o sentido do índice.**

A crítica não é sintática — o código faz exatamente o que está escrito. O problema é que a semântica do filtro contradiz a semântica do índice.

### 3.1 O índice se contradiz internamente

Este é o argumento mais forte, porque não depende de nenhuma suposição externa — está inteiramente dentro do próprio código:

- **24 municípios** estão na base de leitos com `QTD_LEITOS_SUS == 0`. Para eles, `LEITOS_SUS_POR_10MIL = 0` → `SCORE_LEITOS = 0` → **`DEFICIT_LEITOS = 100`** (déficit máximo). **Permanecem no ranking e vão para o topo.**
- **1.976 municípios** não estão na base porque não têm nenhum estabelecimento com leito. Para eles, `LEITOS_SUS_POR_10MIL = NaN` → **descartados.**

Do ponto de vista de um gestor público, esses dois grupos estão na **mesma situação material**: zero leitos SUS disponíveis no território. O pipeline dá ao primeiro grupo prioridade máxima e ao segundo grupo prioridade nenhuma — pela diferença puramente contábil de o CNES manter, ou não, uma linha com valor zero.

Isso não é hipotético: **Palhoça/SC (253.469 hab, 24 UBS, 0 leitos SUS)** é o **2º colocado** do ranking com IPIS 93,32, e **Mirassol/SP (65.811 hab, 0 leitos SUS)** é o **3º** com 92,49. Ambos entram porque têm uma linha zerada. Jandira/SP (121.550 hab), na mesma condição de fato, está fora.

### 3.2 Para leitos, a ausência de registro *é* um zero — não um dado faltante

Este ponto é verificável na própria base: **nenhuma** das 7.208 linhas da competência 202607 tem `LEITOS_EXISTENTES == 0`, e todos os `DS_TIPO_UNIDADE` são hospitais, unidades mistas ou prontos-socorros. A base é, por construção, um cadastro de estabelecimentos **que têm leitos**. Um município ausente não é um município cujo número de leitos é desconhecido — é um município cujo número de leitos é **zero**.

Tratar um zero conhecido como "informação indisponível" e descartá-lo é um erro de codificação de dado, não uma escolha metodológica conservadora. `fillna(0)` aqui é a leitura **correta** da base, não uma imputação otimista.

### 3.3 O filtro remove justamente quem o índice deveria encontrar

Um índice de *prioridade de investimento em infraestrutura* existe para responder: **"onde falta infraestrutura?"**. O filtro atual responde: *"entre os municípios que já têm as duas infraestruturas cadastradas, quem tem menos por habitante?"*. É uma pergunta diferente — e estritamente menos útil.

Quantificando o cenário contrafactual (mesma metodologia, mas com `fillna(0)` em vez de descarte, p95 recalculado sobre os 5.571):

- **92 dos 100 municípios de maior prioridade** do ranking corrigido estão **hoje fora** do `resultado_ipis.csv`.
- **366 dos 500 de maior prioridade** estão hoje fora.
- Os 20 primeiros colocados do ranking corrigido — todos com IPIS 100,0 (Darcinópolis/TO, Presidente Kennedy/TO, Bela Vista do Piauí/PI, Pires Ferreira/CE, Itabi/SE, Tapiraí/MG, Guamiranga/PR, Almirante Tamandaré do Sul/RS, André da Rocha/RS...) — são **todos** municípios atualmente excluídos, os 37 que não têm nem UBS nem leitos.

Ou seja: os municípios em situação mais extrema (nenhuma das duas infraestruturas) são exatamente os que o pipeline apaga. O índice é sistematicamente cego ao pior caso que se propõe a identificar.

### 3.4 O descarte também distorce o score de quem ficou

Os p95 usados na normalização (`05:234-235`) são calculados **sobre a amostra já filtrada**, então a exclusão contamina até os municípios sobreviventes:

| Parâmetro | Amostra filtrada (3.512) | Base completa com `fillna(0)` (5.571) |
|---|---:|---:|
| p95 `UBS_POR_10MIL` | 7,0842 | 8,5300 |
| p95 `LEITOS_SUS_POR_10MIL` | 49,6016 | 41,5055 |

O p95 de leitos cai ~16 % quando a base completa entra. Como `SCORE = valor / p95 * 100`, mudar o denominador **reordena o ranking inteiro** — os déficits atuais não são apenas incompletos, são calibrados contra uma régua enviesada.

### 3.5 A exclusão tem viés geográfico e de porte

Os excluídos não são um sorteio aleatório. São municípios pequenos (mediana 4.989 hab contra a distribuição nacional) e concentrados em MG (447), SP (294), RS (275), PR (167), SC (138). Qualquer agregação estadual — como o `ipis_medio_estados.csv` gerado pelo script 06 — está calculando a **média de uma amostra viesada**, e apresentando o resultado como se fosse o estado.

Concretamente: o IPIS médio de MG hoje é a média de 406 municípios de um total de 853. O ranking de "estados com maior IPIS médio" (`maior_ipis_medios.png`) não é interpretável nessas condições.

### 3.6 A ressalva honesta — o que *não* deve ser feito ingenuamente

Dar déficit 100 aos excluídos é a direção certa, mas há uma nuance que precisa entrar na decisão, porque ignorá-la criaria um erro de sinal oposto:

**Para leitos SUS, o `fillna(0)` é defensável e correto** — pelo argumento de 3.2, a ausência é um zero real.

**Para UBS, `fillna(0)` é arriscado.** Os 83 municípios sem UBS provavelmente têm UBS; 46 deles têm hospital, e Araruama tem 137 mil habitantes. Preencher com 0 daria déficit máximo a municípios cujo problema é o *cadastro*, não a infraestrutura — e eles subiriam ao topo do ranking de investimento por um erro de base. Aqui o correto é **sinalizar** (uma coluna `DADO_UBS_AUSENTE`), não imputar. São dois casos com naturezas diferentes que o filtro atual, por tratar ambos como `NaN`, não consegue distinguir.

**Cuidado adicional com a regionalização.** No SUS, municípios pequenos legitimamente não têm hospital: eles são referenciados a um polo regional pelo Plano Diretor de Regionalização. Dar déficit 100 a todos eles produziria um ranking dominado por municípios de 2 mil habitantes que **não deveriam** ter hospital próprio — trocando um viés (excluir os pequenos) por outro (inundar o topo com eles). O IPIS já tem essa inclinação: a correlação IPIS × população é **+0,17**, e o IPIS médio sobe monotonicamente do quartil menor (39,0) ao maior (66,2)... o que significa que hoje o índice já favorece municípios grandes, e o `fillna(0)` inverteria isso violentamente.

**Conclusão prática:** o descarte está errado e precisa sair, mas a substituição não é um `fillna(0)` de uma linha. A correção defensável tem três partes: (1) `fillna(0)` para leitos, com justificativa documentada; (2) flag de dado ausente para UBS, não imputação; (3) alguma noção de acessibilidade regional para leitos — leitos SUS disponíveis na região de saúde, e não apenas no polígono do município — para que "não tem hospital próprio" e "não tem hospital acessível" deixem de ser a mesma coisa.

---

## 4. Blocos duplicados e redundantes

Verificação feita por hash de cada célula `# %%` (ignorando comentários e linhas em branco), mais inspeção manual.

### 4.1 Duplicações exatas confirmadas

🔴 **`05_integracao_indicadores.py:302-318` e `05:321-337` — bloco `nsmallest` repetido literalmente.**
Foi o caso que você suspeitava. As duas células são **byte-a-byte idênticas** no código:

```python
ipis.nsmallest(10, "IPIS")[["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA",
    "UBS_POR_10MIL", "LEITOS_SUS_POR_10MIL", "SCORE_UBS", "SCORE_LEITOS", "IPIS"]]
```

Só os comentários diferem (`302`: "menores valores de IPIS (menor prioridade de investimento)" / `321`: "menores valores de IPIS"). O segundo bloco é puro copy-paste. **Remover `05:320-337`.**

🔴 **`04_exploracao_leitos.py:157-160` e `04:206-209` — bloco `nlargest` repetido literalmente.**

```python
leitos_por_municipio.nlargest(10, "QTD_LEITOS")
```

Idêntico nos dois pontos, ambos com o comentário *"Identificamos os municípios com maior quantidade de leitos."*. **Remover `04:203-209`.**

### 4.2 Redundâncias de conversão de tipo

🟡 **`05:119-121` e `05:130-132`** — `leitos_sus_por_municipio["CO_IBGE"].astype("string")` é executado **duas vezes** sobre a mesma coluna. A segunda é no-op.

🟡 **`04:176-179` (`astype(str)`) e `04:285-287` (`astype("string")`)** — a mesma coluna `CO_IBGE` é convertida duas vezes, com dtypes diferentes (`object` e depois `StringDtype`). Funciona por acaso; é confuso e frágil.

🟡 **`05:128`** — `municipios["IBGE"].astype("string")` é redundante: a coluna já foi convertida em `05:26`, antes do merge.

### 4.3 Duplicação estrutural entre scripts (o problema maior)

🔴 **O bloco de carga do IBGE está copiado 4 vezes** — `01:11-24`+`01:61`+`01:78-81`, `03:10-29`, `04:9-24`, `05:9-24`. São 4 cópias do mesmo `read_excel` + `notna` + `drop` + construção da chave `IBGE`. Qualquer correção na chave (por exemplo, blindar o `astype(str)` do `COD. UF`) precisa ser aplicada manualmente em 4 lugares — e é exatamente o tipo de coisa que fica dessincronizada.

🔴 **O script 03 é inteiramente redundante em relação ao 05.** `03:62-66` faz o mesmo merge de `05:62-66`; `03:163-167` calcula o mesmo `UBS_POR_10MIL` de `05:78-82`. O 03 não persiste nada — nenhum `to_csv` — então é 100% exploração, mas duplicando lógica de produção do 05. Se a lógica de merge mudar no 05, o 03 vira documentação errada.

🟡 **`05:95-99` relê `Leitos_2026.csv`** (16,7 MB) que o `04` já havia lido e agregado. Cada execução do 05 reprocessa 50.388 linhas do zero. O script 05 tem 1 `read_excel` + 2 `read_csv`.

🟡 **`04:141-145` calcula `QTD_LEITOS` (de `LEITOS_EXISTENTES`) e `04:229-233` calcula `LEITOS_POR_10MIL`** — nenhum dos dois é usado no índice final. O 05 usa apenas `LEITOS_SUS`. É trabalho morto (defensável em um script de exploração, mas vale marcar como tal).

### 4.4 Bug de caminho entre 05 e 06

🔴 **`05:376-380` grava em `"resultado_ipis.csv"`** (raiz do CWD), sem criar diretório:

```python
resultado_ipis.to_csv("resultado_ipis.csv", index=False, encoding="utf-8-sig")
```

🔴 **`06:14-16` lê de `"OUTPUT/resultado_ipis.csv"`**:

```python
ipis = pd.read_csv("OUTPUT/resultado_ipis.csv")
```

**Os caminhos não batem.** O arquivo existe em `OUTPUT/` hoje, o que indica que ele foi movido manualmente após a execução. Rodando o pipeline limpo, o 05 grava na raiz e o **06 quebra com `FileNotFoundError`**. Além disso o 05 não faz `mkdir` de `OUTPUT/` (só o 06 cria `OUTPUT/Analises`).

### 4.5 Outros achados menores

🟡 **`06` não tem células `# %%`**, mas contém expressões nuas (`06:18` `ipis.head()`, `06:21` `ipis.info()`, `06:25` `ipis["IPIS"].describe()`, `06:45` `top10`, `06:113` `distribuicao_faixas`, `06:147` `ipis_estado.head(10)`). Rodando como script `.py`, **essas linhas não produzem saída nenhuma** — são no-ops. Só funcionam em modo interativo.

🟡 **`06` chama `plt.show()` 6 vezes** — em execução não-interativa isso bloqueia o script em cada gráfico.

🟡 **`03:103`** — `ubs[ubs["IBGE"] == 530040]` compara a coluna com um `int` literal. Funciona porque `IBGE` é `int64` na leitura crua, mas quebra silenciosamente (retorna DataFrame vazio, sem erro) se a coluna for convertida para string antes.

🟡 **`04:116` nomeia a variável `leitos_julho`** com a competência hardcoded no nome, enquanto o filtro é dinâmico (`COMP.max()`). Hoje `max = 202607` (julho), então o nome está certo por coincidência. Na próxima atualização da base o nome mente.

🟡 **Truncamento `.str[:6]`** (`03:29`, `04:24`, `05:24`) descarta o dígito verificador do código IBGE. É a decisão certa para casar com as bases do CNES, mas o `resultado_ipis.csv` acaba exportando um código de 6 dígitos que **não é o código IBGE oficial de 7 dígitos** — armadilha para quem for cruzar esse CSV com qualquer outra fonte. Não está documentado em lugar nenhum.

---

## 5. Lista priorizada de correções

### (a) Bugs e duplicações de código

| # | Prio | Item | Local | Ação |
|---|------|------|-------|------|
| a1 | 🔴 Alta | Caminho de saída/entrada incompatível quebra o script 06 | `05:376` ↔ `06:14` | Gravar em `OUTPUT/resultado_ipis.csv` e criar a pasta com `Path("OUTPUT").mkdir(parents=True, exist_ok=True)` |
| a2 | 🔴 Alta | Bloco `nsmallest` duplicado literalmente | `05:320-337` | Remover a segunda ocorrência |
| a3 | 🔴 Alta | Bloco `nlargest(10,"QTD_LEITOS")` duplicado literalmente | `04:203-209` | Remover a segunda ocorrência |
| a4 | 🟡 Média | `astype("string")` repetido sobre `CO_IBGE` | `05:130-132`, `04:285-287` | Remover as conversões redundantes |
| a5 | 🟡 Média | `astype("string")` redundante sobre `IBGE` | `05:128` | Remover (já convertido em `05:26`) |
| a6 | 🟡 Média | Expressões nuas sem efeito em script não-interativo | `06:18,21,25,45,113,147` | Envolver em `print()` ou converter o 06 para células `# %%` |
| a7 | 🟡 Média | `plt.show()` bloqueia execução em lote | `06` (6 ocorrências) | Usar backend `Agg` ou remover os `show()` após o `savefig` |
| a8 | 🟢 Baixa | Variável `leitos_julho` com mês hardcoded no nome | `04:116`, `05:104` | Renomear para `leitos_comp_recente` |
| a9 | 🟢 Baixa | Comparação com literal `int` frágil | `03:103` | Comparar como string ou fixar o dtype antes |
| a10 | 🟢 Baixa | Ausência de asserções sobre a chave | `03/04/05` | `assert len(populacao) == 5571` e `assert populacao["IBGE"].str.len().eq(6).all()` após a construção da chave — pegaria a quebra silenciosa do `COD. UF` float |

### (b) Metodologia — afeta o resultado

| # | Prio | Item | Local | Impacto medido |
|---|------|------|-------|----------------|
| b1 | 🔴 **Crítica** | **Filtro descarta 2.059 municípios (37 %), incluindo os de pior situação** | **`05:201-204`** | 92 dos 100 municípios de maior prioridade real estão fora do CSV; 15,4 M hab (7,22 %) sem ranking |
| b2 | 🔴 **Crítica** | Ausência de leitos tratada como `NaN` quando é um zero conhecido | `05:137-142` → `05:170-174` | Contradição interna: 24 municípios com zero *registrado* vão ao topo; 1.976 na mesma situação de fato são apagados |
| b3 | 🔴 Alta | UBS ausente (83 casos) é lacuna de cadastro, mas indistinguível de zero real | `05:62-66` | 46 desses têm hospital; Araruama tem 137.906 hab. `fillna(0)` aqui seria erro — precisa de flag, não de imputação |
| b4 | 🔴 Alta | p95 calculado sobre a amostra já filtrada contamina quem ficou | `05:234-235` | p95 leitos: 49,60 (filtrado) vs 41,51 (completo) → ~16 % de diferença na régua; reordena o ranking inteiro |
| b5 | 🟡 Média | Uso de uma única competência descarta 6 de 7 meses de dados | `05:104-106` | 17 municípios têm leitos em outros meses e somem em 202607; índice sensível a ruído mensal. Considerar média ou máximo do período |
| b6 | 🟡 Média | Nenhuma noção de acessibilidade regional para leitos | conceito | Municípios pequenos legitimamente não têm hospital (regionalização/PDR). Sem isso, corrigir b1/b2 inunda o topo com municípios de 2 mil hab |
| b7 | 🟡 Média | Índice não pondera população | `05:270-273` | Correlação IPIS × pop = +0,17; IPIS médio Q1 (menores) = 39,0 vs Q4 (maiores) = 66,2. Decidir explicitamente se o ranking é de municípios ou de pessoas afetadas |
| b8 | 🟡 Média | Pesos 50/50 entre UBS e leitos são arbitrários e não documentados | `05:270-273` | Uma UBS e um leito hospitalar não são intercambiáveis em custo nem em impacto |
| b9 | 🟡 Média | Clipping no p95 empilha municípios no mesmo score | `05:237-243` | 176 municípios ficam com `DEFICIT = 0` (empate no fundo) em cada dimensão |
| b10 | 🟢 Baixa | Faixas `[0, 30, 70, 100]` arbitrárias | `05:342-351` | Distribuição resultante: 396 baixa / 2.521 moderada / 595 alta. Cortes por quantil seriam mais defensáveis |
| b11 | 🟢 Baixa | Índice mede só oferta, nunca demanda | conceito | "Prioridade de investimento" sem nenhum proxy de necessidade (perfil etário, mortalidade evitável, renda, distância ao hospital mais próximo) é um índice de oferta per capita com outro nome |
| b12 | 🟢 Baixa | Agregações estaduais calculadas sobre amostra viesada | `06:140-145` | O IPIS médio de MG usa 406 de 853 municípios; o gráfico `maior_ipis_medios.png` não é interpretável até b1 ser resolvido |
| b13 | 🟢 Baixa | Código IBGE truncado em 6 dígitos exportado sem aviso | `05:24` → CSV | O `resultado_ipis.csv` não traz o código IBGE oficial de 7 dígitos; armadilha para cruzamentos futuros |

### (c) Melhorias estruturais

| # | Prio | Item | Ação |
|---|------|------|------|
| c1 | 🔴 Alta | **Sem `requirements.txt` — o pipeline não roda out-of-the-box** | Criar com `pandas`, `matplotlib`, `xlrd` (obrigatório para o `.xls` legado), `openpyxl`. Foi preciso instalar `xlrd` manualmente para esta auditoria |
| c2 | 🔴 Alta | Bloco de carga do IBGE copiado em 4 scripts | Extrair `src/carga.py` com `carregar_populacao()`, `carregar_ubs()`, `carregar_leitos()`. Uma correção de chave passa a ser feita em um lugar só |
| c3 | 🟡 Média | Script 03 duplica a lógica de produção do 05 sem persistir nada | Mover 03 para `exploracao/` (junto com 01, 02, 04) e deixar só o 05 como pipeline de produção — ou fundir os dois |
| c4 | 🟡 Média | Scripts dependem de CWD implícito | Resolver caminhos via `Path(__file__).resolve().parent`, para que rodem de qualquer diretório |
| c5 | 🟡 Média | Sem orquestrador | Criar `run_all.py` ou `Makefile` que rode a sequência de produção na ordem certa e falhe rápido |
| c6 | 🟡 Média | Sem validação de dados | Adicionar checagens em pontos-chave (5.571 municípios, chave de 6 dígitos, 0 duplicatas, cobertura mínima esperada por base) |
| c7 | 🟡 Média | Projeto não está sob controle de versão | `git init` + `.gitignore` (ignorar `OUTPUT/`, `__pycache__/`, `.venv/`; decidir se `RAW/` entra — são 22 MB) |
| c8 | 🟡 Média | README desatualizado e metodologia não documentada | Listar 06 e `OUTPUT/` na estrutura; documentar a fórmula do IPIS, os pesos, a escolha do p95 e — sobretudo — a política de tratamento de ausências decidida em (b) |
| c9 | 🟢 Baixa | Bases `RAW/` sem proveniência | Criar `RAW/FONTES.md` com URL de origem, data de download e competência de cada base |
| c10 | 🟢 Baixa | Sem dicionário de dados da saída | Documentar cada coluna do `resultado_ipis.csv`, incluindo o aviso do código IBGE de 6 dígitos (b13) |
| c11 | 🟢 Baixa | Relê 16,7 MB de CSV a cada execução | Persistir agregados intermediários em `OUTPUT/intermediarios/` (parquet) entre etapas |

---

## Resumo executivo

1. **O funil de linhas está correto até o final.** Os dois merges são `LEFT JOIN` e preservam as 5.571 linhas; a filtragem inicial da população remove apenas 31 linhas de rodapé do arquivo IBGE, corretamente.

2. **Um único ponto do código descarta municípios: `05_integracao_indicadores.py:201-204`.** Ele elimina **2.059 municípios (36,96 %)** e **15,4 milhões de habitantes (7,22 %)** do ranking — 1.976 por falta de leitos SUS, 46 por falta de UBS, 37 por falta de ambos.

3. **A exclusão inverte o propósito do índice.** Os municípios sem nenhuma das duas infraestruturas — os mais carentes — são precisamente os apagados. Num ranking corrigido, **92 dos 100 municípios de maior prioridade estariam hoje fora do arquivo**. E o índice se contradiz: zero leitos *registrado* dá prioridade máxima (Palhoça/SC é 2º colocado), zero leitos *não registrado* dá exclusão.

4. **A correção não é um `fillna(0)` de uma linha.** Para leitos, o zero é real e verificável na base (nenhum estabelecimento com 0 leitos; só hospitais) — `fillna(0)` é correto. Para UBS, é lacuna de cadastro (46 dos 83 têm hospital) — precisa de flag, não de imputação. E sem alguma noção de acessibilidade regional, corrigir o descarte troca o viés contra municípios pequenos por um viés a favor deles.

5. **As duplicações existem e você localizou a certa.** `05:320-337` é copy-paste literal de `05:302-318`. Há uma segunda em `04:203-209`, mais um bug de caminho entre `05:376` e `06:14` que quebra o script 06 numa execução limpa.

**Nada foi corrigido.** Os arquivos do projeto estão intactos; a auditoria rodou em scripts separados fora do repositório.
