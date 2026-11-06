# 👥 Dashboard de RH

Aplicação interativa em **[Streamlit](https://streamlit.io/)** para análise da força de trabalho de uma empresa: quantas pessoas trabalham, quem saiu, quanto se paga e como a equipe está distribuída.

Os dados vêm de uma planilha de funcionários (`data/BaseFuncionarios.xlsx`) e passam por tratamento em **Pandas** antes de virar indicadores e gráficos em **Plotly**.

---

## 🚀 Funcionalidades

O painel tem três abas:

### 🔑 Overview
- Total de funcionários, ativos e desligados.
- Média salarial, idade média e tempo médio de casa.
- Média de horas extras e de férias acumuladas, com uma leitura sobre produtividade e possíveis passivos trabalhistas.

### 📈 Gráficos
- Mapa de funcionários por estado.
- Ativos x desligados por estado.
- Média salarial e tempo médio de casa por área.
- Top 5 salários.
- Distribuição por gênero e por nível.
- Contratações por ano.

### 📂 Dados Tratados
- Tabela completa com as colunas calculadas.
- Download dos dados em CSV.

## 🧹 Tratamento dos dados

- Conversão das datas de nascimento, contratação e demissão.
- Cálculo de **idade**, **tempo de casa** e **status** (ativo ou desligado, a partir da data de demissão).
- Extração de **cidade** e **estado** a partir do endereço, com expressão regular.
- Padronização de sexo (M/F → Masculino/Feminino) e conversão de colunas numéricas.

## 🛠️ Tecnologias

- Python
- Streamlit
- Pandas
- Plotly Express
- OpenPyXL (leitura do Excel)

## ▶️ Como executar

```bash
git clone https://github.com/maribarbalho/dashboard-rh.git
cd dashboard-rh

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install streamlit
pip install -r requirements.txt
streamlit run Dashboard.py
```

---

**Mariana Barbalho** · Data Analytics · [Portfólio](https://maribarbalho.github.io/)
