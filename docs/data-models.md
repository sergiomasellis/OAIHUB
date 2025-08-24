# Data Models

Comprehensive documentation of all data structures, schemas, and models used in the AI Agent Tracking Dashboard.

## 📊 Core Data Models

### AgentEvent

The primary data model for tracking individual events and interactions with AI agents.

#### Schema
```typescript
interface AgentEvent {
  agent_id: string;
  timestamp: string;
  message_type: string;
  content?: string;
  metadata?: Record<string, any>;
  error_details?: string;
  response_time_ms?: number;
  token_count?: number;
  model_used?: string;
  user_feedback?: number;
}
```

#### Python (Pydantic)
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AgentEvent(BaseModel):
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
```

#### Fields Description

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | Yes | Unique identifier for the AI agent |
| `timestamp` | string | Yes | ISO 8601 timestamp (e.g., "2024-01-07T10:30:00Z") |
| `message_type` | string | Yes | Type of event (see Message Types below) |
| `content` | string | No | The actual message content or response |
| `metadata` | object | No | Additional context data as key-value pairs |
| `error_details` | string | No | Error message if applicable |
| `response_time_ms` | number | No | Response time in milliseconds |
| `token_count` | number | No | Number of tokens used in the interaction |
| `model_used` | string | No | AI model used (e.g., "gpt-4", "gpt-3.5-turbo") |
| `user_feedback` | number | No | User rating (1-5 scale) |

#### Message Types

| Type | Description | Example Use Case |
|------|-------------|------------------|
| `user_message` | Message from user to agent | User asks a question |
| `agent_response` | Response from agent to user | Agent provides answer |
| `error` | Error that occurred during processing | API timeout, parsing error |
| `feedback` | User feedback on agent response | User rates response 4/5 |
| `conversation_start` | Start of a conversation session | User initiates chat |
| `conversation_end` | End of a conversation session | User closes chat |
| `graph_step` | Step in a LangGraph execution | Processing node execution |
| `custom_metric` | Custom tracking event | Model confidence score |

### AgentMetrics

Aggregated performance metrics for an agent over a time period.

#### Schema
```typescript
interface AgentMetrics {
  agent_id: string;
  date: string;
  total_messages: number;
  total_responses: number;
  total_errors: number;
  average_response_time: number;
  total_tokens_used: number;
  average_feedback_score: number;
  unique_users: number;
}
```

#### Python (Pydantic)
```python
from pydantic import BaseModel

class AgentMetrics(BaseModel):
    agent_id: str
    date: str
    total_messages: int = 0
    total_responses: int = 0
    total_errors: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    average_feedback_score: float = 0.0
    unique_users: int = 0
```

#### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | string | Unique identifier for the AI agent |
| `date` | string | Date range (e.g., "2024-01-01_to_2024-01-07") |
| `total_messages` | number | Total number of user messages |
| `total_responses` | number | Total number of agent responses |
| `total_errors` | number | Total number of errors |
| `average_response_time` | number | Average response time in milliseconds |
| `total_tokens_used` | number | Total tokens consumed |
| `average_feedback_score` | number | Average user feedback score (1-5) |
| `unique_users` | number | Number of unique users |

### API Response Models

#### AgentEventResponse
```typescript
interface AgentEventResponse {
  event_id: string;
  status: string;
  message: string;
}
```

#### MetricsResponse
```typescript
interface MetricsResponse {
  agent_id: string;
  metrics: AgentMetrics;
  time_range: string;
}
```

## 🗄️ Database Schema

### DynamoDB Tables

#### Events Table (`ai-agent-events`)

**Primary Key:**
- Partition Key: `agent_id` (String)
- Sort Key: `timestamp` (String)

**Global Secondary Index:**
- Index Name: `MessageTypeIndex`
- Partition Key: `message_type` (String)
- Sort Key: `timestamp` (String)
- Projection: `ALL`

**Attributes:**
```json
{
  "agent_id": {"S": "langchain-agent-001"},
  "timestamp": {"S": "2024-01-07T10:30:00Z"},
  "message_type": {"S": "user_message"},
  "content": {"S": "Hello, how are you?"},
  "metadata": {"M": {
    "user_id": {"S": "user-123"},
    "session_id": {"S": "session-456"}
  }},
  "response_time_ms": {"N": "1500"},
  "token_count": {"N": "25"},
  "model_used": {"S": "gpt-4"},
  "user_feedback": {"N": "4"}
}
```

#### Metrics Table (`ai-agent-metrics`)

**Primary Key:**
- Partition Key: `agent_id` (String)
- Sort Key: `date` (String)

**Attributes:**
```json
{
  "agent_id": {"S": "langchain-agent-001"},
  "date": {"S": "2024-01-07"},
  "total_messages": {"N": "150"},
  "total_responses": {"N": "148"},
  "total_errors": {"N": "2"},
  "average_response_time": {"N": "1250.5"},
  "total_tokens_used": {"N": "4500"},
  "average_feedback_score": {"N": "4.2"},
  "unique_users": {"N": "45"}
}
```

## 📈 Data Aggregation Logic

### Daily Metrics Calculation

```python
def calculate_daily_metrics(agent_id: str, date: str) -> AgentMetrics:
    """Calculate daily metrics for an agent"""

    # Query all events for the day
    events = query_events_by_date(agent_id, date)

    metrics = AgentMetrics(
        agent_id=agent_id,
        date=date
    )

    # Count different event types
    for event in events:
        if event.message_type == "user_message":
            metrics.total_messages += 1
        elif event.message_type == "agent_response":
            metrics.total_responses += 1
            if event.response_time_ms:
                # Accumulate for average calculation
                pass
            if event.token_count:
                metrics.total_tokens_used += event.token_count
        elif event.message_type == "error":
            metrics.total_errors += 1
        elif event.message_type == "feedback" and event.user_feedback:
            # Accumulate feedback scores
            pass

    # Calculate averages
    if metrics.total_responses > 0:
        metrics.average_response_time = total_response_time / metrics.total_responses

    if feedback_count > 0:
        metrics.average_feedback_score = total_feedback_score / feedback_count

    # Count unique users from metadata
    user_ids = set()
    for event in events:
        if event.metadata and "user_id" in event.metadata:
            user_ids.add(event.metadata["user_id"])
    metrics.unique_users = len(user_ids)

    return metrics
```

### Real-time Metrics Updates

```python
def update_real_time_metrics(event: AgentEvent):
    """Update real-time metrics cache"""

    # Update in-memory cache
    cache_key = f"metrics:{event.agent_id}:realtime"

    current_metrics = cache.get(cache_key, AgentMetrics(agent_id=event.agent_id))

    if event.message_type == "user_message":
        current_metrics.total_messages += 1
    elif event.message_type == "agent_response":
        current_metrics.total_responses += 1
        if event.response_time_ms:
            # Update rolling average
            current_metrics.average_response_time = update_rolling_average(
                current_metrics.average_response_time,
                event.response_time_ms,
                current_metrics.total_responses
            )
        if event.token_count:
            current_metrics.total_tokens_used += event.token_count
    elif event.message_type == "error":
        current_metrics.total_errors += 1

    cache.set(cache_key, current_metrics, expire=3600)  # 1 hour expiry
```

## 🔄 Data Flow Patterns

### Event Ingestion Flow
1. **AI Agent** generates event data
2. **Validation** against AgentEvent schema
3. **Storage** in DynamoDB Events table
4. **Indexing** for efficient querying
5. **Real-time Updates** to dashboard cache

### Metrics Aggregation Flow
1. **Scheduled Job** runs daily/hourly
2. **Query** events from Events table
3. **Aggregation** using calculation logic
4. **Storage** in Metrics table
5. **Cache Invalidation** for real-time views

### Dashboard Data Flow
1. **User Request** from dashboard
2. **Cache Check** for real-time data
3. **Database Query** if cache miss
4. **Data Processing** and formatting
5. **Response** to frontend

## 📊 Chart Data Models

### Message Volume Chart
```typescript
interface ChartDataPoint {
  date: string;
  messages: number;
  responses: number;
  errors: number;
  responseTime: number;
}
```

### Performance Chart
```typescript
interface PerformanceDataPoint {
  date: string;
  averageResponseTime: number;
  p95ResponseTime: number;
  errorRate: number;
  tokenUsage: number;
}
```

## 🔍 Query Patterns

### Common Queries

#### Get Recent Events
```python
# Query by agent and time range
response = events_table.query(
    KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id) &
                          boto3.dynamodb.conditions.Key('timestamp').between(start_time, end_time)
)
```

#### Get Events by Type
```python
# Use GSI for message type queries
response = events_table.query(
    IndexName='MessageTypeIndex',
    KeyConditionExpression=boto3.dynamodb.conditions.Key('message_type').eq('error') &
                          boto3.dynamodb.conditions.Key('timestamp').between(start_time, end_time)
)
```

#### Get Daily Metrics
```python
# Query metrics for date range
response = metrics_table.query(
    KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id) &
                          boto3.dynamodb.conditions.Key('date').between(start_date, end_date)
)
```

## 🏷️ Metadata Standards

### Standard Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user_id` | string | Unique user identifier | `"user-123"` |
| `session_id` | string | Session identifier | `"session-456"` |
| `conversation_id` | string | Conversation identifier | `"conv-789"` |
| `source` | string | Traffic source | `"web_chat"` |
| `model_version` | string | Model version used | `"gpt-4-v2"` |
| `confidence` | number | Model confidence score | `0.87` |
| `temperature` | number | Model temperature setting | `0.7` |
| `tokens_prompt` | number | Prompt tokens used | `150` |
| `tokens_completion` | number | Completion tokens used | `50` |

### Custom Metadata

```python
# Example custom metadata for LangChain
metadata = {
    "chain_type": "LLMChain",
    "memory_type": "ConversationBufferMemory",
    "tools_used": ["search", "calculator"],
    "llm_config": {
        "temperature": 0.7,
        "max_tokens": 1000,
        "model_name": "gpt-4"
    }
}

# Example custom metadata for LangGraph
metadata = {
    "graph_id": "research-assistant",
    "current_node": "analyze_query",
    "execution_path": ["start", "analyze_query", "search", "summarize"],
    "node_execution_time": {
        "analyze_query": 250,
        "search": 1200,
        "summarize": 800
    }
}
```

## 📋 Data Validation Rules

### Event Validation
```python
def validate_event(event: AgentEvent) -> bool:
    """Validate event data"""

    # Required fields
    if not event.agent_id or not event.timestamp or not event.message_type:
        return False

    # Timestamp format
    try:
        datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
    except ValueError:
        return False

    # Message type validation
    valid_types = {
        "user_message", "agent_response", "error", "feedback",
        "conversation_start", "conversation_end", "graph_step", "custom_metric"
    }
    if event.message_type not in valid_types:
        return False

    # Response time validation
    if event.response_time_ms and event.response_time_ms < 0:
        return False

    # Token count validation
    if event.token_count and event.token_count < 0:
        return False

    # User feedback validation
    if event.user_feedback and not (1 <= event.user_feedback <= 5):
        return False

    return True
```

### Metrics Validation
```python
def validate_metrics(metrics: AgentMetrics) -> bool:
    """Validate metrics data"""

    # Non-negative counts
    if any(count < 0 for count in [
        metrics.total_messages,
        metrics.total_responses,
        metrics.total_errors,
        metrics.total_tokens_used,
        metrics.unique_users
    ]):
        return False

    # Valid averages
    if metrics.average_response_time < 0:
        return False

    if metrics.average_feedback_score < 0 or metrics.average_feedback_score > 5:
        return False

    # Logical consistency
    if metrics.total_responses > metrics.total_messages:
        return False

    if metrics.total_errors > metrics.total_messages:
        return False

    return True
```

## 🔄 Data Migration

### Schema Evolution
When adding new fields to data models:

1. **Backward Compatibility**: Ensure new fields are optional
2. **Default Values**: Provide sensible defaults for new fields
3. **Migration Scripts**: Create scripts to update existing data
4. **Version Tracking**: Track schema versions in metadata

### Example Migration
```python
def migrate_event_schema(event_data: dict) -> dict:
    """Migrate event data to new schema version"""

    # Add new fields with defaults
    event_data.setdefault("model_used", "unknown")
    event_data.setdefault("token_count", 0)
    event_data.setdefault("user_feedback", None)

    # Transform existing fields if needed
    if "old_field" in event_data:
        event_data["new_field"] = transform_old_field(event_data["old_field"])
        del event_data["old_field"]

    return event_data
```

This comprehensive data model documentation provides everything needed to understand, work with, and extend the AI Agent Tracking Dashboard's data structures.