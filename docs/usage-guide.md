# Usage Guide

Complete guide on how to use the AI Agent Tracking Dashboard for monitoring and analyzing AI agent performance.

## 🎯 Dashboard Overview

The AI Agent Tracking Dashboard provides comprehensive insights into your AI agents' performance, usage patterns, and health metrics.

### Main Features
- **Real-time Metrics**: Live monitoring of agent performance
- **Interactive Charts**: Visual representation of key metrics
- **Multi-Agent Support**: Track multiple agents simultaneously
- **Historical Data**: Analyze trends over time
- **Error Tracking**: Monitor and troubleshoot issues
- **Performance Analytics**: Response times, token usage, and more

## 🏠 Dashboard Interface

### Navigation
1. **Header**: Displays the dashboard title and agent selector
2. **Metrics Cards**: Overview of key performance indicators
3. **Charts Section**: Interactive visualizations of metrics over time
4. **Agent Selector**: Dropdown to switch between different agents

### Key Components

#### Agent Selector
- Located in the top-right corner
- Dropdown showing all available agents
- Automatically loads when the page refreshes
- Updates all metrics and charts when changed

#### Metrics Overview Cards
- **Total Messages**: Number of user messages processed
- **Total Responses**: Number of agent responses generated
- **Error Rate**: Percentage of failed interactions
- **Avg Response Time**: Average time to generate responses

#### Performance Charts
- **Message Volume Chart**: Shows messages and responses over time
- **Error & Response Time Chart**: Displays errors and response times
- Interactive tooltips with detailed information
- Zoom and pan capabilities for detailed analysis

## 📊 Understanding Metrics

### Core Metrics

#### Message Volume
- **Total Messages**: Count of all user inputs
- **Total Responses**: Count of all agent outputs
- **Success Rate**: (Responses / Messages) × 100
- **Error Rate**: (Errors / Messages) × 100

#### Performance Metrics
- **Average Response Time**: Mean time for agent responses
- **95th Percentile Response Time**: Ensures 95% of responses are faster
- **Token Usage**: Total tokens consumed by the agent
- **Cost Estimation**: Approximate cost based on token usage

#### Quality Metrics
- **Average Feedback Score**: User ratings (1-5 scale)
- **Error Categories**: Breakdown of different error types
- **Unique Users**: Number of distinct users interacting

### Time-Based Analysis
- **Hourly Trends**: Patterns within a day
- **Daily Trends**: Week-over-week comparisons
- **Monthly Trends**: Long-term performance analysis
- **Peak Usage Times**: Identify high-traffic periods

## 🔧 Integration with AI Agents

### LangChain Integration

#### Basic Integration
```python
from langchain.callbacks.base import BaseCallbackHandler
import requests
import json
from datetime import datetime

class AgentTrackingHandler(BaseCallbackHandler):
    def __init__(self, agent_id: str, api_url: str = "http://localhost:8001/api/v1"):
        self.agent_id = agent_id
        self.api_url = api_url

    def track_event(self, event_type: str, content: str = None, **kwargs):
        """Track an agent event"""
        payload = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": event_type,
            "content": content,
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.api_url}/agents/{self.agent_id}/events",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to track event: {e}")

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        """Called when LLM starts processing"""
        self.track_event(
            "user_message",
            content=prompts[0] if prompts else None,
            metadata={"llm": serialized.get("name", "unknown")}
        )

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes processing"""
        self.track_event(
            "agent_response",
            content=response.generations[0].text if response.generations else None,
            response_time_ms=getattr(response, 'response_time_ms', None),
            token_count=response.llm_output.get("token_usage", {}).get("total_tokens"),
            model_used=response.llm_output.get("model_name")
        )

    def on_llm_error(self, error: Exception, **kwargs):
        """Called when LLM encounters an error"""
        self.track_event(
            "error",
            error_details=str(error),
            metadata={"error_type": type(error).__name__}
        )

# Usage example
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize tracking
tracking_handler = AgentTrackingHandler(agent_id="my-langchain-agent")

# Create LLM with tracking
llm = OpenAI(
    temperature=0.7,
    callbacks=[tracking_handler]
)

# Use in a chain
prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer the following question: {question}"
)

chain = LLMChain(llm=llm, prompt=prompt)
response = chain.run(question="What is the capital of France?")
```

#### Advanced LangChain Integration
```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from typing import Dict, Any

class ComprehensiveAgentTracker:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.session_id = None
        self.conversation_id = None

    def start_conversation(self, user_id: str = None):
        """Start a new conversation session"""
        import uuid
        self.session_id = str(uuid.uuid4())
        self.conversation_id = str(uuid.uuid4())

        self.track_event("conversation_start", metadata={
            "user_id": user_id,
            "session_id": self.session_id,
            "conversation_id": self.conversation_id
        })

    def track_event(self, event_type: str, **kwargs):
        """Enhanced event tracking with session context"""
        payload = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": event_type,
            "metadata": {
                "session_id": self.session_id,
                "conversation_id": self.conversation_id,
                **kwargs.pop("metadata", {})
            },
            **kwargs
        }

        # Send to tracking API
        requests.post(
            f"http://localhost:8001/api/v1/agents/{self.agent_id}/events",
            json=payload
        )

# Initialize comprehensive tracker
tracker = ComprehensiveAgentTracker("advanced-langchain-agent")

# Create agent with tracking
tools = [
    Tool(
        name="Search",
        func=lambda x: f"Search result for: {x}",
        description="Search for information"
    )
]

llm = OpenAI(temperature=0, callbacks=[tracker])
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use with conversation tracking
tracker.start_conversation(user_id="user-123")
result = agent.run("What is the weather like today?")
tracker.track_event("conversation_end", content=result)
```

### LangGraph Integration

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List
import requests
from datetime import datetime

class AgentState(TypedDict):
    messages: List[str]
    current_step: str
    agent_id: str

class LangGraphTracker:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def track_step(self, state: AgentState, step_name: str):
        """Track each step in the graph execution"""
        self._send_event({
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "graph_step",
            "content": f"Executing step: {step_name}",
            "metadata": {
                "step": step_name,
                "current_state": state.get("current_step"),
                "message_count": len(state.get("messages", []))
            }
        })

    def track_completion(self, state: AgentState, result: str):
        """Track graph completion"""
        self._send_event({
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "graph_completion",
            "content": result,
            "metadata": {
                "total_steps": len(state.get("messages", [])),
                "final_state": state.get("current_step")
            }
        })

    def _send_event(self, payload: dict):
        """Send event to tracking API"""
        try:
            requests.post(
                f"http://localhost:8001/api/v1/agents/{self.agent_id}/events",
                json=payload,
                timeout=5
            )
        except Exception as e:
            print(f"Tracking error: {e}")

# Create tracking instance
tracker = LangGraphTracker("langgraph-agent")

# Define graph with tracking
def process_step(state: AgentState) -> AgentState:
    tracker.track_step(state, "process_step")

    # Your processing logic here
    new_message = f"Processed: {state['messages'][-1] if state['messages'] else 'N/A'}"
    state["messages"].append(new_message)
    state["current_step"] = "completed"

    return state

# Build graph
graph = StateGraph(AgentState)
graph.add_node("process", process_step)
graph.set_entry_point("process")

# Compile with tracking
app = graph.compile()

# Use with tracking
initial_state = {
    "messages": ["Hello, world!"],
    "current_step": "starting",
    "agent_id": "langgraph-agent"
}

result = app.invoke(initial_state)
tracker.track_completion(result, str(result))
```

### OpenAI Integration

#### Direct OpenAI API Integration
```python
import openai
import time
import requests
from datetime import datetime

class OpenAITracker:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        openai.api_key = "your-api-key"

    def track_completion(self, messages, model="gpt-4", **kwargs):
        """Track OpenAI completion with metrics"""
        start_time = time.time()

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                **kwargs
            )

            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)

            # Track successful completion
            self._send_event({
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": "agent_response",
                "content": response.choices[0].message.content,
                "response_time_ms": response_time_ms,
                "token_count": response.usage.total_tokens,
                "model_used": model,
                "metadata": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            })

            return response

        except Exception as e:
            # Track error
            self._send_event({
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": "error",
                "error_details": str(e),
                "metadata": {"error_type": type(e).__name__}
            })
            raise

    def _send_event(self, payload: dict):
        """Send event to tracking API"""
        requests.post(
            f"http://localhost:8001/api/v1/agents/{self.agent_id}/events",
            json=payload
        )

# Usage
tracker = OpenAITracker("openai-agent")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

response = tracker.track_completion(messages, model="gpt-4")
```

### Custom AI Agent Integration

```python
import requests
from datetime import datetime
from typing import Dict, Any

class AgentTracker:
    """Generic agent tracking utility"""

    def __init__(self, agent_id: str, api_url: str = "http://localhost:8001/api/v1"):
        self.agent_id = agent_id
        self.api_url = api_url

    def track_interaction(self,
                         user_input: str,
                         agent_response: str = None,
                         response_time_ms: int = None,
                         tokens_used: int = None,
                         model: str = None,
                         error: Exception = None,
                         metadata: Dict[str, Any] = None):
        """Track a complete interaction"""

        events = []

        # Track user message
        events.append({
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "user_message",
            "content": user_input,
            "metadata": metadata or {}
        })

        if error:
            # Track error
            events.append({
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": "error",
                "error_details": str(error),
                "metadata": {
                    "error_type": type(error).__name__,
                    **(metadata or {})
                }
            })
        elif agent_response:
            # Track successful response
            events.append({
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": "agent_response",
                "content": agent_response,
                "response_time_ms": response_time_ms,
                "token_count": tokens_used,
                "model_used": model,
                "metadata": metadata or {}
            })

        # Send all events
        for event in events:
            try:
                requests.post(
                    f"{self.api_url}/agents/{self.agent_id}/events",
                    json=event,
                    timeout=5
                )
            except Exception as e:
                print(f"Failed to track event: {e}")

# Usage example
tracker = AgentTracker("custom-agent")

def process_user_query(user_input: str) -> str:
    """Example custom agent function"""
    start_time = time.time()

    try:
        # Your AI processing logic here
        response = f"Response to: {user_input}"

        response_time = int((time.time() - start_time) * 1000)

        # Track successful interaction
        tracker.track_interaction(
            user_input=user_input,
            agent_response=response,
            response_time_ms=response_time,
            tokens_used=25,  # Estimate
            model="custom-model-v1",
            metadata={"confidence": 0.95}
        )

        return response

    except Exception as e:
        # Track error
        tracker.track_interaction(
            user_input=user_input,
            error=e,
            metadata={"stage": "processing"}
        )
        raise

# Use the tracked agent
result = process_user_query("Hello, how are you?")
```

## 📈 Analyzing Dashboard Data

### Performance Analysis

#### Response Time Analysis
1. **Identify Slow Periods**: Look for spikes in response time charts
2. **Compare Models**: Track performance across different AI models
3. **Load Impact**: Monitor how response times change with load
4. **Optimization Opportunities**: Find consistently slow interactions

#### Error Analysis
1. **Error Patterns**: Identify common error types and times
2. **Error Rates**: Monitor error rates over time
3. **Recovery Time**: Track time to resolve error conditions
4. **Root Cause Analysis**: Use metadata to identify error sources

### Usage Patterns

#### User Behavior Analysis
1. **Peak Usage Times**: Identify when users are most active
2. **Query Patterns**: Analyze common user questions
3. **Session Length**: Track user engagement duration
4. **Drop-off Points**: Identify where users stop interacting

#### Agent Performance
1. **Success Rates**: Monitor successful vs failed interactions
2. **Token Efficiency**: Track token usage per interaction
3. **Cost Analysis**: Calculate costs based on token usage
4. **Quality Metrics**: Monitor user feedback trends

### Trend Analysis

#### Long-term Trends
1. **Growth Patterns**: Track user and message volume growth
2. **Performance Trends**: Monitor improvements over time
3. **Seasonal Patterns**: Identify weekly/monthly usage patterns
4. **Model Performance**: Compare performance across model updates

#### Anomaly Detection
1. **Sudden Changes**: Alert on significant metric changes
2. **Performance Degradation**: Monitor for gradual performance decline
3. **Error Spikes**: Detect unusual error rate increases
4. **Usage Anomalies**: Identify unusual usage patterns

## 🔧 Advanced Features

### Custom Metrics

You can extend the tracking to include custom metrics specific to your use case:

```python
def track_custom_metrics(agent_id: str, custom_data: dict):
    """Track custom metrics"""
    payload = {
        "agent_id": agent_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message_type": "custom_metric",
        "metadata": custom_data
    }

    requests.post(
        f"http://localhost:8001/api/v1/agents/{agent_id}/events",
        json=payload
    )

# Example: Track model confidence scores
track_custom_metrics("my-agent", {
    "metric_type": "confidence_score",
    "value": 0.87,
    "threshold": 0.8,
    "model_version": "v2.1"
})
```

### Batch Tracking

For high-volume scenarios, you can batch events:

```python
def batch_track_events(agent_id: str, events: list):
    """Track multiple events in batch"""
    for event in events:
        event["agent_id"] = agent_id
        event["timestamp"] = event.get("timestamp", datetime.utcnow().isoformat())

        requests.post(
            f"http://localhost:8001/api/v1/agents/{agent_id}/events",
            json=event
        )
```

### Real-time Monitoring

For real-time monitoring, you can poll the API:

```javascript
// Frontend real-time updates
setInterval(async () => {
  try {
    const response = await fetch('/api/v1/agents/current-agent/metrics?days=1');
    const data = await response.json();
    updateDashboard(data);
  } catch (error) {
    console.error('Failed to fetch metrics:', error);
  }
}, 30000); // Update every 30 seconds
```

## 📊 Exporting Data

### API Data Export
```bash
# Export metrics for a specific agent
curl "http://localhost:8001/api/v1/agents/agent-1/metrics?days=30" \
  -H "Accept: application/json" \
  -o agent_metrics.json

# Export all agents
curl "http://localhost:8001/api/v1/agents" \
  -o agents_list.json
```

### Chart Data Export
1. Use browser developer tools to copy chart data
2. Export as CSV from the dashboard interface
3. Use the API to fetch raw data for custom analysis

## 🚨 Alerts and Monitoring

### Setting Up Alerts

You can implement custom alerts based on metrics:

```python
def check_alerts(agent_id: str):
    """Check for alert conditions"""
    response = requests.get(f"http://localhost:8001/api/v1/agents/{agent_id}/metrics?days=1")
    metrics = response.json()["metrics"]

    alerts = []

    # Error rate alert
    if metrics["total_messages"] > 0:
        error_rate = metrics["total_errors"] / metrics["total_messages"]
        if error_rate > 0.05:  # 5% error rate
            alerts.append(f"High error rate: {error_rate:.1%}")

    # Response time alert
    if metrics["average_response_time"] > 10000:  # 10 seconds
        alerts.append(f"Slow response time: {metrics['average_response_time']}ms")

    # Low feedback alert
    if metrics["average_feedback_score"] < 3.0:
        alerts.append(f"Low feedback score: {metrics['average_feedback_score']}/5")

    return alerts

# Check alerts periodically
alerts = check_alerts("my-agent")
if alerts:
    print("ALERTS:", alerts)
    # Send notifications, emails, etc.
```

## 📈 Best Practices

### Data Collection
1. **Consistent Agent IDs**: Use consistent, descriptive agent identifiers
2. **Rich Metadata**: Include relevant context in metadata fields
3. **Error Details**: Provide detailed error information for debugging
4. **Performance Metrics**: Track all relevant performance indicators

### Dashboard Usage
1. **Regular Monitoring**: Check dashboard daily for performance issues
2. **Trend Analysis**: Look for patterns over time, not just snapshots
3. **Comparative Analysis**: Compare metrics across different agents
4. **Actionable Insights**: Focus on metrics that drive improvements

### Integration
1. **Error Handling**: Implement proper error handling in tracking code
2. **Async Tracking**: Don't let tracking failures break your main application
3. **Rate Limiting**: Implement appropriate rate limiting for tracking calls
4. **Data Validation**: Validate data before sending to tracking API

This comprehensive usage guide should help you effectively integrate the AI Agent Tracking Dashboard into your AI systems and make the most of its monitoring and analytics capabilities.