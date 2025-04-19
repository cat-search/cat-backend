#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 15:43:56 2025

@author: dmitriykruglov
"""



import uuid
from functools import partial
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi import FastAPI
import asyncio
import logging
import torch
import weaviate
from weaviate.auth import AuthApiKey
from typing import List, Dict, Any, Optional
from functools import lru_cache
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import Weaviate
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document
from uuid import uuid4
import time
from weaviate import Client

# --- Конфигурация ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceConfig(BaseModel):
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    dtype: Optional[str] = "float16" if torch.cuda.is_available() else None
    embeddings_batch_size: int = 128 if torch.cuda.is_available() else 32

# --- Модели данных ---
class QueryRequest(BaseModel):
    text: str
    stream: bool = False

class QueryResponse(BaseModel):
    query_id: str
    status: str  # "processing"|"completed"|"failed"
    answer: Optional[str] = None
    sources: Optional[List[str]] = None
    latency_ms: Optional[int] = None


# --- RAGLogger (улучшенная версия) ---
class RAGLogger:
    def __init__(self, name: str = "RAG"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Настройка формата без дублирования handlers"""
        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s | %(context)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, level: str, message: str, **context):
        self.logger.log(
            getattr(logging, level.upper()),
            message,
            extra={"context": context}
        )

    info = lambda self, msg, **ctx: self.log("INFO", msg, **ctx)
    error = lambda self, msg, **ctx: self.log("ERROR", msg, **ctx)


# --- OptimizedRAGSystem ---
class OptimizedRAGSystem:
    def __init__(self):
        """Инициализация только общих компонентов"""
        self.logger = RAGLogger("RAG.Core")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._init_weaviate_client()

    def _init_weaviate_client(self):
        """Только подключение к Weaviate"""
        try:
            self.client = weaviate.WeaviateClient(
                connection_params=weaviate.ConnectionParams.from_params(
                    http_host="localhost",
                    http_port=8080,
                    http_secure=False,
                    grpc_host="none",
                    grpc_port=50051,
                    grpc_secure=False
                ),
                auth_client_secret=AuthApiKey("ollama"),
                additional_headers={"X-Ollama-Api-Key": "ollama"}
            )
            if not self.client.is_live():
                raise ConnectionError("Weaviate недоступен")
            self.logger.info("Weaviate подключен")
        except Exception as e:
            self.logger.error("Ошибка подключения Weaviate", error=str(e))
            raise

    async def initialize_embeddings(self):
        """Инициализация моделей эмбеддингов"""
        try:
            self.embeddings = (
                OllamaEmbeddings(model="nomic-embed-text") 
                if self.device == "cpu" 
                else HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            )
            self.logger.info("Эмбеддинги инициализированы", model=self.embeddings.model_name)
        except Exception as e:
            self.logger.error("Ошибка инициализации эмбеддингов", error=str(e))
            raise

    async def chunk_documents(self, texts: List[str]) -> List[Document]:
        """Чанкование документов с обработкой ошибок"""
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = splitter.create_documents(texts)
            self.logger.info("Документы разбиты на чанки", chunks_count=len(chunks))
            return chunks
        except Exception as e:
            self.logger.error("Ошибка чанкования", error=str(e))
            raise

    async def setup_weaviate_collection(self, collection: str, chunks: List[Document]):
        """Настройка коллекции в Weaviate"""
        try:
            if not self.client.collections.exists(collection):
                self.client.collections.create(
                    name=collection,
                    properties=[{"name": "content", "dataType": ["text"]}],
                    vectorizer_config=weaviate.Configure.Vectorizer.none()
                )
                self.logger.info("Коллекция создана", collection=collection)

            with self.client.batch as batch:
                for chunk in chunks:
                    batch.add_data_object(
                        collection_name=collection,
                        data_object={
                            "content": chunk.page_content,
                            "metadata": chunk.metadata
                        },
                        vector=self.embeddings.embed_query(chunk.page_content)
                    )
            self.logger.info("Данные загружены в Weaviate", count=len(chunks))
        except Exception as e:
            self.logger.error("Ошибка работы с Weaviate", error=str(e))
            raise

    async def build_qa_chain(self, collection: str):
        """Сборка QA цепочки LangChain"""
        try:
            prompt_template = """Ответь строго по контексту:
            Контекст: {context}
            Вопрос: {question}
            Требования:
            1. Ответ до 3 предложений
            2. Если ответа нет - скажи "Не знаю\""""
            
            self.vectorstore = Weaviate(
                client=self.client,
                index_name=collection,
                text_key="content",
                embedding=self.embeddings
            )

            self.qa_chain = RetrievalQA.from_chain_type(
                llm=Ollama(model="mistral", temperature=0.3),
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                chain_type_kwargs={
                    "prompt": PromptTemplate.from_template(prompt_template),
                    "verbose": False
                }
            )
            self.logger.info("QA цепочка создана")
        except Exception as e:
            self.logger.error("Ошибка создания QA цепочки", error=str(e))
            raise

    async def full_initialization(self, texts: List[str], collection: str = "Docs"):
        """Полная инициализация системы"""
        await self.initialize_embeddings()
        chunks = await self.chunk_documents(texts)
        await self.setup_weaviate_collection(collection, chunks)
        await self.build_qa_chain(collection)

    async def query(self, question: str) -> Dict:
        """Выполнение запроса с метриками"""
        query_id = str(uuid4())
        start_time = time.time()
        
        try:
            self.logger.info("Начало обработки запроса", query_id=query_id)
            result = await self.qa_chain.acall({"query": question})
            
            latency = int((time.time() - start_time)*1000)
            self.logger.info(
                "Запрос выполнен",
                query_id=query_id,
                latency_ms=latency,
                answer_length=len(result["result"])
            )
            
            return {
                "answer": result["result"],
                "sources": [doc.metadata.get("source") for doc in result["source_documents"]],
                "latency_ms": latency
            }
        except Exception as e:
            self.logger.error("Ошибка запроса", query_id=query_id, error=str(e))
            raise

# --- FastAPI интеграция ---

app = FastAPI()
rag = OptimizedRAGSystem()

@app.on_event("startup")
async def startup():
    from langchain.document_loaders import TextLoader
    texts = TextLoader("data.txt").load()
    await rag.initialize_components(texts)

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Комбинированная версия с:
    - Поддержкой стриминга (флаг)
    - Детальным статусом
    - Метрикой latency
    """
    query_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Для стриминга - фоновая задача
        if request.stream:
            background_tasks.add_task(
                rag.process_query_async,
                question=request.text,
                query_id=query_id
            )
            return QueryResponse(
                query_id=query_id,
                status="processing"
            )
        
        # Синхронный ответ
        result = await rag.query(request.text)
        return QueryResponse(
            query_id=query_id,
            status="completed",
            answer=result["answer"],
            sources=result["sources"],
            latency_ms=int((time.time() - start_time)*1000)
        )
        
    except Exception as e:
        logger.error("API error", error=str(e), query_id=query_id)
        raise HTTPException(
            status_code=500,
            detail={
                "query_id": query_id,
                "error": str(e),
                "status": "failed"
            }
        )



# @app.post("/query", response_model=QueryResponse)
# async def query_endpoint(request: QueryRequest):
#     query_id = str(uuid4())
#     start_time = time.time()
    
#     try:
#         result = await rag.query(request.text)
#         return QueryResponse(
#             query_id=query_id,
#             status="completed",
#             answer=result["answer"],
#             sources=result["sources"],
#             latency_ms=int((time.time() - start_time)*1000)
#         )
#     except Exception as e:
#         raise HTTPException(500, detail=str(e))