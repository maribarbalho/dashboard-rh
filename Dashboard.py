import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# =================== CONFIGURAÇÕES INICIAIS ===================
st.set_page_config(
    page_title="DASHBOARD DE RH 👥",
    layout="wide"
)

# Função auxiliar para formatar valores numéricos
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


# =================== CARREGAMENTO E TRATAMENTO DE DADOS ===================
@st.cache_data
def carregar_dados():
    url = 'https://api.sheet2db.com/v1/9ade87a1-0fa4-4dab-b816-e2bc305b7f81'
    response = requests.get(url)
    df = pd.DataFrame.from_dict(response.json())

    hoje = pd.to_datetime("today").normalize()

    # Tratamento de datas
    df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento'], errors='coerce').dt.normalize()
    df['Data de Contratacao'] = pd.to_datetime(df['Data de Contratacao'], errors='coerce').dt.normalize()
    df['Data de Demissao'] = pd.to_datetime(df['Data de Demissao'], errors='coerce').dt.normalize()

    # Colunas adicionais
    df["Tempo de Casa"] = ((hoje - df['Data de Contratacao']).dt.days) // 365
    df["Sexo"] = df["Sexo"].map({"M": "Masculino", "F": "Feminino"})
    df[['Cidade', 'Estado']] = df['Endereço'].str.extract(r',\s*([^,]+)\s*-\s*([A-Z]{2})')
    df['Status'] = df['Data de Demissao'].apply(lambda x: 'Desativado' if pd.notna(x) else 'Ativo')

    # Conversões numéricas
    df["Salario Base"] = pd.to_numeric(df["Salario Base"], errors="coerce")
    df["Horas Extras"] = pd.to_numeric(df["Horas Extras"], errors="coerce")
    df["Ferias Acumuladas"] = pd.to_numeric(df["Ferias Acumuladas"], errors="coerce")

    # Ajuste de colunas de data
    df['Data de Nascimento'] = df['Data de Nascimento'].dt.date
    df['Data de Contratacao'] = df['Data de Contratacao'].dt.date
    df['Data de Demissao'] = df['Data de Demissao'].dt.date

    return df, hoje

df, hoje = carregar_dados()


# =================== FUNÇÕES DE VISUALIZAÇÃO ===================
def mostrar_overview(df, hoje):
    st.subheader("Visão Geral 🔑")
    st.markdown("""
    Este painel apresenta uma **visão geral** da força de trabalho da empresa,
    destacando os principais indicadores de **pessoas** e **produtividade**.
    """)

    # --- Pessoas ---
    st.subheader("📊 Pessoas")
    st.markdown("A empresa conta atualmente com os seguintes números de colaboradores:")

    df["Idade"] = ((hoje - pd.to_datetime(df["Data de Nascimento"], errors="coerce")).dt.days / 365).round()
    df["Tempo de Casa"] = ((hoje - pd.to_datetime(df["Data de Contratacao"], errors="coerce")).dt.days / 365).round()

    total_funcionarios = df.shape[0]
    ativos = df[df["Status"] == "Ativo"].shape[0]
    desligados = df[df["Status"] == "Desativado"].shape[0]
    perc_ativos = (ativos / total_funcionarios) * 100 if total_funcionarios > 0 else 0
    perc_desligados = (desligados / total_funcionarios) * 100 if total_funcionarios > 0 else 0
    idade_media = df["Idade"].mean()
    tempo_medio_casa = round(df["Tempo de Casa"].mean())
    media_salarial = df["Salario Base"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Funcionários", total_funcionarios)
    col2.metric("Ativos", f"{ativos}")
    col3.metric("Desligados", f"{desligados}")
    col4.metric("Média Salarial", formata_numero(media_salarial, "R$"))

    st.markdown(f"""
    Atualmente, **{perc_ativos:.1f}%** da força de trabalho está ativa, enquanto **{perc_desligados:.1f}%** já foi desligada.  
    A **idade média** dos colaboradores é de **{round(idade_media)} anos**, e o **tempo médio de casa** é de **{tempo_medio_casa} anos**.
    """)

    st.markdown("---")

    # --- Produtividade ---
    st.subheader("⚖️ Produtividade")
    st.markdown("A produtividade pode ser observada pelo acúmulo de férias e pelas horas extras realizadas:")

    media_horas_extras = round(df["Horas Extras"].mean())
    media_ferias = round(df["Ferias Acumuladas"].mean())

    col5, col6 = st.columns(2)
    col5.metric("Média de Horas Extras", f"{media_horas_extras}h")
    col6.metric("Média de Férias Acumuladas", f"{media_ferias} dias")

    st.markdown(f"""
    Em média, cada colaborador acumula **{media_horas_extras} horas extras**
    e **{media_ferias} dias de férias**.  
    Esses números podem indicar tanto **dedicação além da carga horária**
    quanto **acúmulo de passivos trabalhistas**.
    """)


def mostrar_graficos(df):
    st.subheader("📈 Gráficos")

    # --- Mapa por Estado ---
    df_estado = df.groupby("Estado").size().reset_index(name="Qtd Funcionários")
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

    fig_mapa = px.choropleth(
        df_estado,
        geojson=geojson_url,
        locations="Estado",
        featureidkey="properties.sigla",
        color="Qtd Funcionários",
        color_continuous_scale="Blues",
        scope="south america",
        title="Funcionários por Estado"
    )
    fig_mapa.update_geos(scope="south america", projection_type="mercator")

    st.plotly_chart(fig_mapa, use_container_width=True)

    # --- Média Salarial por Área ---
    media_salarial_area = df.groupby("Área")["Salario Base"].mean().sort_values(ascending=False).reset_index()
    fig_media_salarial_area = px.line(
        media_salarial_area.head(),
        x='Área',
        y='Salario Base',
        markers=True,
        title='Média Salarial por Área',
        color_discrete_sequence=["#c97fd7"]
    )
    st.plotly_chart(fig_media_salarial_area, use_container_width=True)


def mostrar_dados(df):
    st.subheader("📂 Dados Tratados")
    st.dataframe(df)


# =================== DASHBOARD PRINCIPAL ===================
st.title('DASHBOARD DE RH 👥')

aba1, aba2, aba3 = st.tabs(['🔑 Overview', '📈 Gráficos', '📂 Dados Tratados'])

with aba1:
    mostrar_overview(df, hoje)

with aba2:
    mostrar_graficos(df)

with aba3:
    mostrar_dados(df)
