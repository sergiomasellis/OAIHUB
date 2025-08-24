# API Reference

Complete API documentation for the AI Agent Tracking Dashboard backend.

## Base URL

```
http://localhost:8001/api/v1
```

## Authentication

Currently, no authentication is required. For production deployments, consider implementing API key authentication.

## Endpoints

### Health Check

#### GET /health

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200` - API is healthy
- `500` - API is unhealthy

---

### Agent Management

#### GET /agents

List all tracked agents.

**Response:**
```json
[
  "agent-1",
  "agent-2",
  "langchain-agent-001"
]
```

**Status Codes:**
- `200` - Success
- `500` - Internal server error

---

#### GET /agents/{agent_id}/metrics

Get aggregated metrics for a specific agent.

**Parameters:**
- `agent_id` (path): Unique identifier for the agent
- `days` (query, optional): Number of days to look back (default: 7)
- `start_date` (query, optional): Start date in YYYY-MM-DD format
- `end_date` (query, optional): End date in YYYY-MM-DD format

**Example Request:**
```bash
GET /api/v1/agents/agent-1/metrics?days=30
```

**Response:**
```json
{
  "agent_id": "agent-1",
  "metrics": {
    "agent_id": "agent-1",
    "date": "2024-01-01_to_2024-01-07",
    "total_messages": 1250,
    "total_responses": 1240,
    "total_errors": 10,
    "average_response_time": 850.5,
    "total_tokens_used": 45000,
    "average_feedback_score": 4.2,
    "unique_users": 156
  },
  "time_range": "2024-01-01 to 2024-01-07"
}
```

**Status Codes:**
- `200` - Success
- `404` - Agent not found
- `500` - Internal server error

---

#### POST /agents/{agent_id}/events

Record a new event for an agent.

**Parameters:**
- `agent_id` (path): Unique identifier for the agent

**Request Body:**
```json
{
  "agent_id": "agent-1",
  "timestamp": "2024-01-07T10:30:00Z",
  "message_type": "user_message",
  "content": "Hello, can you help me with a question?",
  "metadata": {
    "user_id": "user-123",
    "session_id": "session-456",
    "conversation_id": "conv-789"
  },
  "response_time_ms": null,
  "token_count": null,
  "model_used": null,
  "user_feedback": null
}
```

**Response:**
```json
{
  "event_id": "evt-123456789",
  "status": "success",
  "message": "Event recorded successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request data
- `500` - Internal server error

---

## Data Models

### AgentEvent

Represents an individual event or interaction with an AI agent.

**Properties:**
- `agent_id` (string, required): Unique identifier for the agent
- `timestamp` (string, required): ISO 8601 timestamp
- `message_type` (string, required): Type of event
  - `user_message`: Message from user to agent
  - `agent_response`: Response from agent to user
  - `error`: Error that occurred during processing
  - `feedback`: User feedback on agent response
- `content` (string, optional): The actual message content
- `metadata` (object, optional): Additional context data
- `error_details` (string, optional): Error message if applicable
- `response_time_ms` (number, optional): Response time in milliseconds
- `token_count` (number, optional): Number of tokens used
- `model_used` (string, optional): AI model used (e.g., "gpt-4", "gpt-3.5-turbo")
- `user_feedback` (number, optional): User rating (1-5 scale)

### AgentMetrics

Aggregated performance metrics for an agent over a time period.

**Properties:**
- `agent_id` (string): Unique identifier for the agent
- `date` (string): Date range in format "YYYY-MM-DD_to_YYYY-MM-DD"
- `total_messages` (number): Total number of user messages
- `total_responses` (number): Total number of agent responses
- `total_errors` (number): Total number of errors
- `average_response_time` (number): Average response time in milliseconds
- `total_tokens_used` (number): Total tokens consumed
- `average_feedback_score` (number): Average user feedback score (1-5)
- `unique_users` (number): Number of unique users interacting with the agent

### AgentEventResponse

Response format for event recording operations.

**Properties:**
- `event_id` (string): Unique identifier for the recorded event
- `status` (string): Operation status ("success" or "error")
- `message` (string): Human-readable status message

### MetricsResponse

Response format for metrics retrieval operations.

**Properties:**
- `agent_id` (string): Agent identifier
- `metrics` (AgentMetrics): The metrics data
- `time_range` (string): Date range for the metrics

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error details"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting to prevent abuse.

---

## Content Types

- **Request**: `application/json`
- **Response**: `application/json`

---

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for web applications. The following headers are included:

- `Access-Control-Allow-Origin`: Configurable (default: *)
- `Access-Control-Allow-Methods`: GET, POST, OPTIONS
- `Access-Control-Allow-Headers`: Content-Type, Authorization

---

## Integration Examples

### Python (LangChain/LangGraph)

```python
import requests
import json
from datetime import datetime

def track_agent_event(agent_id, event_type, content, **kwargs):
    """Track an agent event"""
    url = f"http://localhost:8001/api/v1/agents/{agent_id}/events"

    payload = {
        "agent_id": agent_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message_type": event_type,
        "content": content,
        **kwargs
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to track event: {e}")
        return None

# Example usage in LangChain callback
class AgentTrackingCallback:
    def on_llm_start(self, serialized, prompts, **kwargs):
        track_agent_event(
            agent_id="langchain-agent-001",
            message_type="user_message",
            content=prompts[0],
            metadata={"llm": serialized.get("name")}
        )

    def on_llm_end(self, response, **kwargs):
        track_agent_event(
            agent_id="langchain-agent-001",
            message_type="agent_response",
            content=response.generations[0].text,
            token_count=response.llm_output.get("token_usage", {}).get("total_tokens"),
            model_used=response.llm_output.get("model_name")
        )

    def on_llm_error(self, error, **kwargs):
        track_agent_event(
            agent_id="langchain-agent-001",
            message_type="error",
            error_details=str(error)
        )
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8001/api/v1';

async function trackAgentEvent(agentId, eventData) {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/agents/${agentId}/events`,
      {
        agent_id: agentId,
        timestamp: new Date().toISOString(),
        ...eventData
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to track event:', error);
    throw error;
  }
}

// Example usage
async function handleUserMessage(agentId, userMessage) {
  // Track user message
  await trackAgentEvent(agentId, {
    message_type: 'user_message',
    content: userMessage,
    metadata: {
      source: 'web_chat',
      user_id: getCurrentUserId()
    }
  });

  // Process with AI agent
  const response = await processWithAI(userMessage);

  // Track agent response
  await trackAgentEvent(agentId, {
    message_type: 'agent_response',
    content: response.text,
    response_time_ms: response.duration,
    token_count: response.tokenCount,
    model_used: response.model
  });

  return response;
}
```

### cURL

```bash
# Track a user message
curl -X POST http://localhost:8001/api/v1/agents/agent-1/events \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-1",
    "timestamp": "2024-01-07T10:30:00Z",
    "message_type": "user_message",
    "content": "Hello, how are you?",
    "metadata": {
      "user_id": "user-123",
      "session_id": "session-456"
    }
  }'

# Get agent metrics
curl "http://localhost:8001/api/v1/agents/agent-1/metrics?days=7"

# List all agents
curl http://localhost:8001/api/v1/agents
```

---

## Webhooks (Future Enhancement)

For real-time integrations, webhooks can be configured to notify external systems when certain events occur:

- Agent error rate exceeds threshold
- Response time degradation
- High token usage alerts
- New agent registration

---

## Versioning

The API uses URL-based versioning (`/api/v1/`). Future versions will be added as `/api/v2/`, etc., while maintaining backward compatibility where possible.