# 🌤️ Pipeline ETL — Weather Data

> Pipeline ETL orquestrado com **Apache Airflow** que extrai dados climáticos da **OpenWeather API**, transforma com **Pandas** e carrega no **PostgreSQL** — automatizado via Docker.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%20|%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Airflow-3.3.1-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white" alt="Airflow">
  <img src="https://img.shields.io/badge/Postgres-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="Postgres">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Pandas-3.0-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
</p>

---

## 📖 Sobre

Projeto prático de **Engenharia de Dados** que implementa um pipeline ETL completo para dados meteorológicos de **Goiânia - GO**.

A cada hora o Airflow dispara a DAG `weather_pipeline` que coleta a temperatura, umidade, vento, pressão e outras métricas atuais via OpenWeather, normaliza os dados e persiste no banco para análises futuras.

```
  [ OpenWeather API ] ──► [ Extract ] ──► [ Transform ] ──► [ Load → PostgreSQL ]
                               ▲                  ▲                    ▲
                               └──────────────── Airflow DAG ──────────┘
                                           (a cada 1 hora)
```

---

## 🧱 Stack

| Camada | Tecnologia |
|---|---|
| **Orquestração** | Apache Airflow 3.3.1 (LocalExecutor + Standalone) |
| **Banco** | PostgreSQL 16 |
| **Extração** | `requests` + OpenWeather API 2.5 |
| **Transformação** | `pandas` + `json_normalize` |
| **Carga** | `SQLAlchemy` + `psycopg2-binary` |
| **Infra** | Docker & Docker Compose |
| **Gerenciador** | `uv` |

---

## 📂 Estrutura

```
projeto_pipeline_weather/
├── dags/
│   └── weather_dag.py        # DAG weather_pipeline (extract → transform → load)
├── src/
│   ├── extract_data.py       # consome a API e salva weather_data.json
│   ├── transform_data.py     # normaliza weather, renomeia colunas, converte timestamps
│   └── load_data.py          # grava no Postgres via SQLAlchemy
├── data/
│   ├── weather_data.json     # raw da API
│   └── temp_data.parquet     # intermediário entre transform e load
├── config/
│   └── .env                  # API_KEY_WEATHER + credenciais Postgres
├── init-db/                  # scripts de inicialização do banco aula_weather
├── docker-compose.yaml
├── pyproject.toml
└── main.py                   # runner local (opcional)
```

---

## ⚙️ Como rodar

### 1. Pré-requisitos

- Docker e Docker Compose
- Chave gratuita da [OpenWeather API](https://openweathermap.org/api)

### 2. Configurar variáveis

Crie o arquivo `config/.env`:

```env
API_KEY_WEATHER=sua_chave_aqui
POSTGRES_HOST=postgres
POSTGRES_DB=aula_weather
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=123456
```

> A DAG também lê `API_KEY_WEATHER` do ambiente do container.

### 3. Subir o ambiente

```bash
docker compose up --build
```

- Airflow UI: **http://localhost:8000** → login `airflow` / senha no log do container `airflow`
- Postgres: `localhost:5433` → DB `airflow` (metastore) e `aula_weather` (dados)

### 4. Ativar a DAG

1. Acesse o Airflow UI
2. Ative a DAG `weather_pipeline`
3. Clique em **Trigger DAG** para rodar manualmente ou aguarde o schedule `0 */1 * * *` (a cada hora)

### 5. Conferir os dados

```bash
docker compose exec postgres psql -U weather_user -d aula_weather -c "SELECT city_name, temperature, humidity, wind_speed, datetime FROM go_weather ORDER BY datetime DESC LIMIT 5;"
```

### Rodar local sem Docker (opcional)

```bash
uv sync
uv run python src/extract_data.py
uv run python -c "from src.transform_data import data_transformations; print(data_transformations().head())"
```

---

## 🔄 O que cada etapa faz

| Etapa | Arquivo | O que faz |
|---|---|---|
| **Extract** | `src/extract_data.py:27` | `GET https://api.openweathermap.org/...?q=GOIANIA,BR` → salva `data/weather_data.json` |
| **Transform** | `src/transform_data.py:91` | `json_normalize` + explode `weather[0]` + `drop` + `rename` + converte `dt/sunrise/sunset` para `America/Sao_Paulo` |
| **Load** | `src/load_data.py:50` | `df.to_sql("go_weather", if_exists="append")` + validação com `SELECT COUNT` |

---

## 🙏 Créditos

Este projeto foi desenvolvido a partir da videoaula da **Luiza Vieira — vbluuiza**.

> 🔊 *Leia a descrição para mergulhar no universo dos dados!*  
> *Neste canal, compartilho conteúdos sobre engenharia de dados, pipelines, Airflow, dbt, SQL, Python e muito mais! Se você quer aprender de forma simples e direta como funciona o ecossistema de dados, aqui é o lugar certo.*

**Criadora original:**

- 👩‍💻 **Luiza Vieira** — [@vbluuiza](https://github.com/vbluuiza)
- 📂 Repositório original: [pipeline_etl_weather_data_tutorial_youtube](https://github.com/vbluuiza/pipeline_etl_weather_data_tutorial_youtube)
- 🎥 Canal no YouTube: [@vbluuiza](https://www.youtube.com/@vbluuiza)
- 💼 LinkedIn: [linkedin.com/in/vbluuiza](https://www.linkedin.com/in/vbluuiza)

**Links citados no vídeo:**

- 📄 Documentação completa do projeto (Google Docs) — link no vídeo original
- 🔀 Padrão de Commits: [Guia no Notion](https://fair-organ-4e1.notion.site/Guia-de-Padrao-de-Commits-553a7d8f95b2494e98474d0b8d2386c5)

> Se este repositório te ajudou, deixe uma ⭐ e se inscreva no canal da Luiza: https://www.youtube.com/@vbluuiza

---

## 📝 Licença

Este projeto é de uso educacional. Créditos ao material original devem ser mantidos. Verifique a licença do repositório base da autora para reuso comercial.

---

<p align="center">Feito com ☕ e dados • Goiânia, GO 🇧🇷</p>
