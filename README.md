# 📊 Dashboard de Vendas e Dados Brutos

Este projeto é uma aplicação interativa construída com **[Streamlit](https://streamlit.io/)** para análise e visualização de dados de vendas.  

O sistema consome dados de uma API pública fictícia (`https://labdados.com/produtos`) e apresenta:  
- **Dashboard de Vendas**: visualizações interativas de receita, quantidade de vendas e desempenho dos vendedores.  
- **Dados Brutos**: interface para explorar, filtrar e exportar os dados em formato CSV.  

---

## 🚀 Funcionalidades

### Dashboard de Vendas
- Filtros por região, ano e vendedores.  
- Visualização de **receita e quantidade de vendas** por:  
  - Estado  
  - Mês  
  - Categoria de produto  
  - Vendedores  
- Gráficos interativos com **Plotly**.  
- Métricas em tempo real.  

### Dados Brutos
- Exibição da tabela completa de dados.  
- Filtros avançados (produto, categoria, preço, frete, vendedor, data, avaliação, tipo de pagamento, etc.).  
- Seleção de colunas para exibição.  
- Exportação dos dados filtrados em **CSV**.  

---

## 🛠️ Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)  
- [Streamlit](https://streamlit.io/)  
- [Pandas](https://pandas.pydata.org/)  
- [Plotly Express](https://plotly.com/python/plotly-express/)  
- [Requests](https://docs.python-requests.org/)  


## ▶️ Como executar o projeto

```bash
git clone https://github.com/maribarbalho/dashboard_vendas.git
cd dashboard_vendas

python -m venv .venv
# Ativar ambiente virtual:
# Linux/Mac: source .venv/bin/activate
# Windows: .venv\Scripts\activate

# Após criação do ambiente virtual execute os comandos abaixo via terminal:
pip install streamlit
pip install -r requirements.txt
streamlit run Dashboard.py