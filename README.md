# Overview

Бэкенд проекта CatSearch

# Algo

Модули проекта:
- Front
  - User query. Log query
- VectorDB
  - Embed user query
  - Search VectorDB. Log doc ids and duration
- Reranker
  - Rerank documents
- LLM
  - Query LLM. Log query, response, and duration


# Structure

```text
.
.
├── doc                     # Other docs
├── src                     # Весь source code
│   ├── core
│   │   ├── db.py           # Postgresql 
│   │   ├── log.py          # Logging
│   │   ├── settings.py     # Application settings
│   ├── front               # User-side interactions: with front UI
│   ├── llm                 # LLM interactions: ollama
│   ├── migrations          # Alembic migrations
│   ├── models              # Postgresql models (sqlalchemy)
│   ├── schemas             # Pydantic schemas
│   └── vectordb            # Vector DB: weaviate, marqo, ...
├── Dockerfile
├── main.py                 # Application main program file
├── poetry.lock             # poetry
├── pyproject.toml          # poetry
├── README.md               # Main README

```

# Local development

Swagger:
- http://127.0.0.1:8000/docs


