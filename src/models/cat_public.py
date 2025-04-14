from enum import Enum

from sqlalchemy import (
    Column,
    Index,
)
from sqlalchemy.dialects.postgresql import (
    UUID, TIMESTAMP, TEXT, JSONB, INTERVAL,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class QueryStatus(Base):
    """ Статусы запросов """
    __tablename__ = 'backend_query_status'
    __table_args__ = (
        {
            'schema': 'public',
            'comment': 'Статусы запросов',
        },
    )
    query_id  = Column(UUID, primary_key=True, comment='ID запроса')
    # status: We'll use text, easier to debug
    status    = Column(TEXT, comment='Статус запроса')
    timestamp = Column(TIMESTAMP, comment='Timestamp получения запроса')


Index(None, QueryStatus.timestamp.desc(), unique=False)


class QueryDetail(Base):
    """ Детали запросы """
    __tablename__ = 'backend_query_detail'
    __table_args__ = (
        {
            'schema': 'public',
            'comment': 'Детали запросов',
        },
    )
    query_id       = Column(UUID, primary_key=True, comment='ID запроса')
    query_text     = Column(TEXT, comment='Статус запроса')
    timestamp      = Column(TIMESTAMP, comment='Timestamp получения запроса')
    total_latency  = Column(INTERVAL, comment='Полное время от получения запрос до ответ')
    vdb            = Column(TEXT, comment='Vector DB name')
    vdb_index      = Column(TEXT, comment='Vector DB index/collection name')
    vdb_latency    = Column(INTERVAL, comment='Длительность ответа vector DB')
    llm_model      = Column(TEXT, comment='LLM model name')
    llm_latency    = Column(INTERVAL, comment='Длительность ответа LLM')
    rnk_model      = Column(TEXT, comment='Reranker model name')
    rnk_latency    = Column(INTERVAL, comment='Длительность ответа reranker')
    info           = Column(JSONB, comment='Прочая информация')


Index(None, QueryDetail.timestamp.desc(), unique=False)


class Status(str, Enum):
    """
    Статусы запроса
    Не будем париться с Enum, INT. Так нагляднее.
    """
    # new        = 0
    # vdb_start  = 1
    # vdb_done   = 2
    # rnk_start  = 3
    # rnk_done   = 4
    # llm_start  = 5
    # llm_done   = 6
    # done       = 7
    # error      = 8
    new        = 'new'
    vdb_start  = 'vdb_start'
    vdb_done   = 'vdb_done'
    rnk_start  = 'rnk_start'
    rnk_done   = 'rnk_done'
    llm_start  = 'llm_start'
    llm_done   = 'llm_done'
    done       = 'done'
    error      = 'error'
