from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AgentEvent(BaseModel):
    """Model for individual agent events (messages, responses, errors)"""
    agent_id: str
    timestamp: str
    message_type: str  # 'user_message', 'agent_response', 'error', 'feedback'
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    response_time_ms: Optional[int] = None
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    user_feedback: Optional[int] = None  # Rating 1-5

class AgentMetrics(BaseModel):
    """Model for aggregated metrics"""
    agent_id: str
    date: str  # YYYY-MM-DD format
    total_messages: int = 0
    total_responses: int = 0
    total_errors: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    average_feedback_score: float = 0.0
    unique_users: int = 0

class AgentEventResponse(BaseModel):
    """Response model for event ingestion"""
    event_id: str
    status: str = "success"
    message: str = "Event recorded successfully"

class MetricsResponse(BaseModel):
    """Response model for metrics queries"""
    agent_id: str
    metrics: AgentMetrics
    time_range: str

class DashboardKPI(BaseModel):
    title: str
    value: float
    change: float
    changeType: str  # 'increase' | 'decrease'
    description: Optional[str] = None

class DashboardKPIsResponse(BaseModel):
    start_date: str
    end_date: str
    agents: Optional[list[str]] = None
    kpis: list[DashboardKPI]

class EventItem(BaseModel):
    agent_id: str
    timestamp: str
    message_type: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    response_time_ms: Optional[int] = None
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    user_feedback: Optional[int] = None

class EventsResponse(BaseModel):
    items: list[EventItem]
    next_key: Optional[Dict[str, Any]] = None

class SeriesPoint(BaseModel):
    date: str  # YYYY-MM-DD
    calls: int
    errors: int
    visitors: int  # unique users/visitors
    models: list[str] = []  # Available models for this date
    model_usage: dict[str, int] = {}  # Usage count per model

class MetricsSeriesResponse(BaseModel):
    start_date: str
    end_date: str
    agents: Optional[list[str]] = None
    items: list[SeriesPoint]

class ConversationItem(BaseModel):
    id: str
    agent_id: str
    startedAt: str
    duration: int
    messageCount: int
    status: str  # completed | active | error

class ConversationsResponse(BaseModel):
    items: list[ConversationItem]

class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    start_time: str
    end_time: Optional[str] = None
    status: Optional[str] = None
    service_name: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class TraceIngestRequest(BaseModel):
    spans: list[TraceSpan]

class TraceDetailResponse(BaseModel):
    trace_id: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_ms: Optional[int] = None
    spans: list[TraceSpan]
