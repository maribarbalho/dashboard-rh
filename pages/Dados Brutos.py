import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="DADOS BRUTOS", layout="wide")


# Carrega a planilha original, sem tratamento (mesma base do Dashboard)
@st.cache_data
def carregar_dados_brutos():
    caminho = Path(__file__).parent.parent / "data" / "BaseFuncionarios.xlsx"
    dados = pd.read_excel(caminho)
    dados["Data de Contratacao"] = pd.to_datetime(dados["Data de Contratacao"], errors="coerce").dt.date
    dados["Data de Nascimento"] = pd.to_datetime(dados["Data de Nascimento"], errors="coerce").dt.date
    dados["Data de Demissao"] = pd.to_datetime(dados["Data de Demissao"], errors="coerce").dt.date
    return dados


# Função para converter o DataFrame em CSV e armazenar em cache (evita recomputar)
@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode("utf-8")


# Mensagem exibida ao baixar o arquivo
def mensagem_sucesso():
    st.toast("Arquivo baixado com sucesso!", icon="✅")


# Título da aplicação
st.title("DADOS BRUTOS")

dados = carregar_dados_brutos()

# Seletor de colunas para exibir na tabela (expansível)
with st.expander("Colunas"):
    colunas = st.multiselect("Selecione as colunas", list(dados.columns), list(dados.columns))

# ==========================
# Barra lateral de filtros
# ==========================
st.sidebar.title("Filtros")

with st.sidebar.expander("Área"):
    areas = st.multiselect("Selecione as áreas", sorted(dados["Área"].dropna().unique()), sorted(dados["Área"].dropna().unique()))

with st.sidebar.expander("Nível"):
    niveis = st.multiselect("Selecione os níveis", sorted(dados["Nível"].dropna().unique()), sorted(dados["Nível"].dropna().unique()))

with st.sidebar.expander("Cargo"):
    cargos = st.multiselect("Selecione os cargos", sorted(dados["Cargo"].dropna().unique()), sorted(dados["Cargo"].dropna().unique()))

with st.sidebar.expander("Sexo"):
    sexos = st.multiselect("Selecione o sexo", sorted(dados["Sexo"].dropna().unique()), sorted(dados["Sexo"].dropna().unique()))

with st.sidebar.expander("Status"):
    status = st.radio("Exibir funcionários", ["Todos", "Ativos", "Desligados"])

with st.sidebar.expander("Salário base"):
    sal_min, sal_max = int(dados["Salario Base"].min()), int(dados["Salario Base"].max())
    salario = st.slider("Faixa salarial (R$)", sal_min, sal_max, (sal_min, sal_max))

with st.sidebar.expander("Data de contratação"):
    data_min, data_max = dados["Data de Contratacao"].min(), dados["Data de Contratacao"].max()
    data_contratacao = st.date_input("Selecione o período", (data_min, data_max), min_value=data_min, max_value=data_max)

# ==========================
# Aplicação dos filtros
# ==========================
filtro = (
    dados["Área"].isin(areas)
    & dados["Nível"].isin(niveis)
    & dados["Cargo"].isin(cargos)
    & dados["Sexo"].isin(sexos)
    & dados["Salario Base"].between(salario[0], salario[1])
)

if status == "Ativos":
    filtro &= dados["Data de Demissao"].isna()
elif status == "Desligados":
    filtro &= dados["Data de Demissao"].notna()

# O seletor de datas devolve só uma data enquanto o período está sendo escolhido
if isinstance(data_contratacao, tuple) and len(data_contratacao) == 2:
    filtro &= dados["Data de Contratacao"].between(data_contratacao[0], data_contratacao[1])

# Mantém apenas as linhas filtradas e as colunas selecionadas
dados_filtrados = dados[filtro][colunas]

# Exibe a tabela filtrada
st.dataframe(dados_filtrados)

# Mostra a quantidade de linhas e colunas resultantes
st.markdown(f"A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas")

# ==========================
# Download da tabela
# ==========================
st.markdown("Escreva um nome para o arquivo")
coluna1, coluna2 = st.columns(2)

with coluna1:
    # Campo de texto para nome do arquivo
    nome_arquivo = st.text_input("Nome do arquivo", label_visibility="collapsed", value="dados")
    nome_arquivo += ".csv"

with coluna2:
    # Botão para baixar o arquivo CSV com os filtros aplicados
    st.download_button(
        "Fazer o download da tabela em csv",
        data=converte_csv(dados_filtrados),
        file_name=nome_arquivo,
        mime="text/csv",
        on_click=mensagem_sucesso,
    )
