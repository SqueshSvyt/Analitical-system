from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Custom JSON encoder for Neo4j types
def serialize_neo4j_datetime(obj):
    """Convert Neo4j DateTime to ISO format string"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj


# ============== Node Models ==============

class Article(BaseModel):
    article_id: str
    title: str
    published_date: datetime
    source: str
    link: str


class Event(BaseModel):
    event_id: str
    type: str  # e.g., "Conflict.Attack", "Diplomacy.Sanction"
    trigger_word: str
    confidence: float = Field(ge=0.0, le=1.0)
    article_id: str


class Entity(BaseModel):
    entity_id: str
    text: str
    label: str  # GPE, ORG, PERSON, DATE, etc.


# ============== Request Models ==============

class EventFilterRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    min_confidence: float = 0.0
    limit: int = 100


class EntitySearchRequest(BaseModel):
    query: str
    label: Optional[str] = None
    limit: int = 50


class StorylineRequest(BaseModel):
    event_pattern: List[str]  # e.g., ["Conflict.Attack", "Diplomacy.Sanction", "Diplomacy.Meeting"]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_days_between_events: int = 30
    limit: int = 20


class QARequest(BaseModel):
    query: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AlertConfigRequest(BaseModel):
    alert_type: str  # "spike", "escalation", "novelty", "evidence"
    event_types: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    threshold: Optional[float] = None


# ============== Response Models ==============

class EventResponse(BaseModel):
    event_id: str
    type: str
    trigger_word: str
    confidence: float
    article_id: str
    article_title: Optional[str] = None
    published_date: Optional[datetime] = None
    entities: List[str] = []


class EventTrendPoint(BaseModel):
    date: str
    event_type: str
    count: int


class EntityOverviewResponse(BaseModel):
    entity_id: str
    text: str
    label: str
    total_events: int
    event_distribution: Dict[str, int]
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class EntityTimelineEvent(BaseModel):
    event_id: str
    event_type: str
    date: datetime
    article_title: str
    confidence: float


class EntityNetworkNode(BaseModel):
    entity_id: str
    text: str
    label: str
    connection_count: int


class EntityNetworkResponse(BaseModel):
    nodes: List[EntityNetworkNode]
    edges: List[Dict[str, Any]]


class StorylineChain(BaseModel):
    chain_id: str
    events: List[Dict[str, Any]]
    entities: List[str]
    confidence: float
    time_span_days: int


class Alert(BaseModel):
    alert_id: str
    alert_type: str
    severity: str  # "low", "medium", "high"
    title: str
    description: str
    triggered_at: datetime
    related_events: List[str] = []
    related_entities: List[str] = []
    supporting_articles: List[str] = []


class QAResponse(BaseModel):
    query: str
    answer: str
    evidence: List[Dict[str, Any]]
    related_entities: List[str]
    related_events: List[str]

