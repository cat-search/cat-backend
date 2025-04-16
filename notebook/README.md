# Weaviate + Ollama RAG System

🚀 Реализация RAG-системы с Weaviate (v3) и Ollama (Mistral/Nomic)

## 📦 Зависимости
```bash
pip install -r requirements.txt
```

## 🛠 Настройка
1. Запустите Weaviate локально:
```bash
docker-compose up -d
```

2. Убедитесь, что Ollama работает:
```bash
ollama pull mistral
ollama pull nomic-embed-text
```

## 🚀 Использование
```python
from src.rag_system import RAGSystem

rag = RAGSystem()
rag.initialize_weaviate()
rag.load_and_process_file("your_file.txt")
results = rag.query("Ваш вопрос")
```

## 📚 Библиотеки
- Weaviate Client: `3.26.7`
- LangChain: `0.1.14`
- Ollama: `0.1.8`