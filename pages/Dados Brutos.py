import streamlit as st
import requests
import pandas as pd
import time

# Função para converter o DataFrame em CSV e armazenar em cache (evita recomputar)
@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# Função para exibir mensagem de sucesso ao baixar o arquivo
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)   # espera 5 segundos
    sucesso.empty() # limpa a mensagem depois

# Título da aplicação
st.title('DADOS BRUTOS')

# Requisição dos dados da API
url = 'https://api.sheet2db.com/v1/9ade87a1-0fa4-4dab-b816-e2bc305b7f81'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())

# Conversão da coluna de data para datetime
# dados['Data de Contratacao'] = pd.to_datetime(dados['Data de Contratacao'], format = '%d/%m/%Y')

# Seletor de colunas para exibir na tabela (expansível)
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# ==========================
# Barra lateral de filtros
# ==========================
st.sidebar.title('Filtros')

with st.sidebar.expander('ID RH'):
    produtos = st.multiselect('Selecione o ID', dados['ID RH'].unique(), dados['ID RH'].unique())

# with st.sidebar.expander('Categoria do produto'):
#     categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

# with st.sidebar.expander('Preço do produto'):
#     preco = st.slider('Selecione o preço', 0, 5000, (0,5000))

# with st.sidebar.expander('Frete da venda'):
#     frete = st.slider('Frete', 0,250, (0,250))

# with st.sidebar.expander('Data da compra'):
#     data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

# with st.sidebar.expander('Vendedor'):
#     vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

# with st.sidebar.expander('Local da compra'):
#     local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

# with st.sidebar.expander('Avaliação da compra'):
#     avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))

# with st.sidebar.expander('Tipo de pagamento'):
#     tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

# with st.sidebar.expander('Quantidade de parcelas'):
#     qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# ==========================
# Filtro com query
# ==========================

# String com a condição para filtrar os dados (usando query do pandas)
query = '''
Produto in @Nome Completo and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

# Aplica os filtros nos dados
dados_filtrados = dados.query(query)

# Mantém apenas as colunas selecionadas
dados_filtrados = dados_filtrados[colunas]

# Exibe a tabela filtrada
st.dataframe(dados_filtrados)

# Mostra a quantidade de linhas e colunas resultantes
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

# ==========================
# Download da tabela
# ==========================
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)

with coluna1:
    # Campo de texto para nome do arquivo
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'

with coluna2:
    # Botão para baixar o arquivo CSV com os filtros aplicados
    st.download_button('Fazer o download da tabela em csv', 
                       data = converte_csv(dados_filtrados), 
                       file_name = nome_arquivo, 
                       mime = 'text/csv', 
                       on_click = mensagem_sucesso)