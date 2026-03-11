# AI Tech Stocks Platform

Backend RESTful em FastAPI para dados de ações de empresas de tecnologia relacionadas a IA, com dashboard analítico em Streamlit.

## Objetivos do projeto

1. Expor dados de mercado de ações via API REST.
2. Restringir o domínio para empresas tech com forte relação com IA.
3. Organizar o código com boas práticas de engenharia.
4. Disponibilizar um dashboard detalhado para análise.

## Stack

1. Python 3.11+
2. FastAPI
3. Uvicorn
4. yfinance
5. Streamlit
6. Plotly
7. Pytest

## Arquitetura

```text
app/
  api/
    dependencies.py
    routers/
      health.py
      stocks.py
  core/
    config.py
  schemas/
    stock.py
  services/
    stock_service.py
  main.py
streamlit_app/
  dashboard.py
tests/
  test_api.py
```

### Padrões aplicados

1. Separação por camadas (API, serviço, schemas, configuração).
2. Injeção de dependência para facilitar testes.
3. Modelos de entrada e saída com Pydantic.
4. Tratamento de erro de domínio com tradução para HTTP status code.
5. Testes de API desacoplados de provedores externos por uso de serviço fake.

## Tickers monitorados

A API monitora por padrão:

1. NVDA
2. MSFT
3. GOOGL
4. AMD
5. TSM
6. AVGO
7. AMZN
8. META
9. ASML

## Configuração

1. Copie as variáveis de ambiente:

```bash
cp .env.example .env
```

2. Instale dependências com `uv`:

```bash
uv sync
```

Se preferir `pip`:

```bash
pip install -e .[dev]
```

## Execução da API

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação interativa:

1. Swagger UI: `http://localhost:8000/docs`
2. ReDoc: `http://localhost:8000/redoc`

## Endpoints REST

Base path: `/api/v1`

1. `GET /health`
   Retorna status da aplicação.
2. `GET /stocks`
   Lista tickers monitorados.
3. `GET /stocks/{symbol}`
   Retorna resumo do ativo.
4. `GET /stocks/{symbol}/history?period=3mo&interval=1d`
   Retorna histórico OHLCV do ativo.

## Execução do dashboard

Com a API rodando:

```bash
uv run streamlit run streamlit_app/dashboard.py
```

Painel disponibiliza:

1. Filtro por ticker.
2. Filtro por período e intervalo.
3. KPIs de preço, market cap, máxima e mínima.
4. Gráfico candlestick com médias móveis de 20 e 50 períodos.
5. Gráfico de volume.
6. Série de retorno diário percentual.
7. Tabela com histórico recente.

## Testes

```bash
uv run pytest
```

## Qualidade de código

Lint:

```bash
uv run ruff check .
```

## Próximas evoluções recomendadas

1. Adicionar cache distribuído para reduzir chamadas ao Yahoo Finance.
2. Implementar autenticação e rate limiting.
3. Persistir snapshots históricos em banco de dados.
4. Adicionar métricas operacionais e observabilidade.
