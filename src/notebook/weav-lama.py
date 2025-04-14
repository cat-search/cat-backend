#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 15:43:56 2025

@author: dmitriykruglov
"""




import ollama
from langchain_ollama import OllamaEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Weaviate
from langchain_community.llms.ollama import Ollama as OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import weaviate
import logging
from typing import List, Optional
import os

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    def __init__(self):
        self.client = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
    
    def initialize_weaviate(self) -> weaviate.Client:
        """Инициализация подключения (Weaviate v3)"""
        try:
            self.client = weaviate.Client(
                url="http://localhost:8080",
                additional_headers={"X-Ollama-Api-Key": "ollama"}
            )
            logger.info("✅ Успешное подключение к Weaviate (v3)")
            return self.client
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {str(e)}")
            raise
    
    def load_and_process_file(self, file_path: str):
        """Загрузка и обработка файла"""
        try:
            # 1. Загрузка документа
            logger.info(f"Загрузка файла: {file_path}")
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            # 2. Разбивка на чанки
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                separators=["\n\n", "\n", r"(?<=\. )", " ", ""]
            )
            texts = text_splitter.split_documents(documents)
            logger.info(f"Создано {len(texts)} чанков")
            return texts
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {str(e)}")
            raise
    
    def initialize_components(self, texts: List, collection_name: str = "Documents"):
        """Инициализация RAG (исправленная версия для Weaviate v3)"""
        try:
            # 1. Проверка моделей Ollama (без изменений)
            logger.info("Проверка моделей Ollama...")
            for model in ["nomic-embed-text", "mistral"]:
                try:
                    ollama.show(model)
                except:
                    logger.warning(f"Модель {model} не найдена, скачиваю...")
                    ollama.pull(model)
            
            # 2. Инициализация эмбеддингов
            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            
            # 3. Загрузка в Weaviate
            logger.info(f"Создание коллекции {collection_name} в Weaviate...")
            
            # Получаем текущую схему для проверки
            current_schema = self.client.schema.get()
            class_exists = any(cls["class"] == collection_name for cls in current_schema.get("classes", []))
            
            if not class_exists:
                class_obj = {
                    "class": collection_name,
                    "properties": [{
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Текст документа"
                    }],
                    "vectorizer": "none"
                }
                self.client.schema.create_class(class_obj)
                logger.info(f"Коллекция {collection_name} создана")
            
            # 4. Инициализация VectorStore с batch_size
            self.vectorstore = Weaviate.from_documents(
                client=self.client,
                documents=texts,
                embedding=embeddings,
                index_name=collection_name,
                text_key="content",
                by_text=False,
                batch_size=50  # <-- ДОБАВЛЕНО ЗДЕСЬ
            )
            
            # 5. Инициализация LLM (без изменений)
            self.llm = OllamaLLM(
                model="mistral",
                temperature=0.3,
                system="Ты - помощник, отвечающий на вопросы по документам."
            )
            
            template = """Ответь на вопрос, используя ТОЛЬКО предоставленный контекст.
            Контекст: {context}
            Вопрос: {question}
            Чёткий ответ:"""
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]  # Явно указываем переменные
            )
            
            # 6. Создание цепочки QA (с явным указанием document_variable_name)
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                chain_type_kwargs={
                    "prompt": prompt,
                    "document_variable_name": "context"  # Важно!
                },
                return_source_documents=True
            )
            
            logger.info("✅ RAG система успешно инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {str(e)}")
            raise

    def query(self, question: str) -> dict:
        """Выполнение запроса к RAG системе"""
        try:
            if not self.qa_chain:
                raise ValueError("RAG система не инициализирована")
            
            result = self.qa_chain.invoke({"query": question})
            return {
                "answer": result["result"],
                "sources": [doc.page_content for doc in result["source_documents"]]
            }
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {str(e)}")
            raise
    
    def test_system(self):
        """Тестирование работоспособности системы"""
        try:
            # Тест поиска
            test_results = self.vectorstore.similarity_search("тест", k=1)
            logger.info(f"Тест поиска: {test_results[0].page_content[:100]}...")
            
            # Тест LLM
            test_response = self.llm.invoke("Что такое RAG? Ответь кратко.")
            logger.info(f"Тест LLM: {test_response[:100]}...")
            
            # Тест полной цепочки
            test_qa = self.query("Тестовый вопрос")
            logger.info(f"Тест QA: {test_qa['answer'][:100]}...")
            
            return True
        except Exception as e:
            logger.error(f"Тест провален: {str(e)}")
            return False


# Пример использования
if __name__ == "__main__":
    # Инициализация системы
    rag = RAGSystem()
    rag.initialize_weaviate()
    
    # Обработка файла (можно заменить на любой другой .txt файл)
    input_file = "/Users/dmitriykruglov/Downloads/Хладнокровное-убийство.doc.txt"
    processed_texts = rag.load_and_process_file(input_file)
    
    # Инициализация RAG
    rag.initialize_components(processed_texts, collection_name="CrimeBook")
    
    # Проверка работоспособности
    if rag.test_system():
        print("✅ Система работает корректно")
        
        # Пример запроса
        while True:
            question = input("\nВведите ваш вопрос (или 'exit' для выхода): ")
            if question.lower() == 'exit':
                break
                
            result = rag.query(question)
            print("\nОтвет:", result["answer"])
            print("\nИсточники:")
            for i, source in enumerate(result["sources"], 1):
                print(f"{i}. {source[:200]}...")
    else:
        print("❌ Обнаружены проблемы в работе системы")
