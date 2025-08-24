# Architecture Overview

This document provides a comprehensive overview of the AI Agent Tracking Dashboard architecture, including system design, components, data flow, and technical decisions.

## 🏗️ System Architecture

The AI Agent Tracking Dashboard follows a modern microservices architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   DynamoDB      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│                 │    │                 │    │                 │
│ - Dashboard     │    │ - REST API      │    │ - Events Table  │
│ - Charts        │    │ - Data Models   │    │ - Metrics Table │
│ - Real-time     │    │ - Business Logic│    │ - Aggregations  │
│ - Salt DS       │    │ - CORS Support  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Docker Compose │
                    │  (Orchestration)│
                    └─────────────────┘
```

## 🧩 Component Details

### Frontend (React + TypeScript)

**Technology Stack:**
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **ShadCn UI**: Consistent, accessible UI components
- **Recharts**: Data visualization library
- **Axios**: HTTP client for API communication

**Key Components:**
- `Dashboard`: Main dashboard page with metrics overview
- `AgentSelector`: Dropdown for agent selection
- `MetricsChart`: Interactive charts using Recharts
- `apiService`: Centralized API communication layer

**State Management:**
- React hooks for local component state
- Context API for global application state
- Real-time updates via API polling

### Backend (FastAPI + Python)

**Technology Stack:**
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Boto3**: AWS SDK for DynamoDB integration
- **Python-dotenv**: Environment variable management

**API Structure:**
```
api/v1/
├── agents/
│   ├── GET /agents                    # List all agents
│   ├── GET /agents/{agent_id}/metrics # Get agent metrics
│   └── POST /agents/{agent_id}/events # Record agent event
└── health/
    └── GET /health                    # Health check
```

**Data Models:**
- `AgentEvent`: Individual agent interactions
- `AgentMetrics`: Aggregated performance data
- `AgentEventResponse`: API response format

### Database (DynamoDB)

**Table Structure:**

#### Events Table (`ai-agent-events`)
```json
{
  "agent_id": "string (Partition Key)",
  "timestamp": "string (Sort Key)",
  "message_type": "string (GSI Partition Key)",
  "content": "string",
  "metadata": "object",
  "error_details": "string",
  "response_time_ms": "number",
  "token_count": "number",
  "model_used": "string",
  "user_feedback": "number"
}
```

**Global Secondary Index:**
- `MessageTypeIndex`: For querying by message type

#### Metrics Table (`ai-agent-metrics`)
```json
{
  "agent_id": "string (Partition Key)",
  "date": "string (Sort Key)",
  "total_messages": "number",
  "total_responses": "number",
  "total_errors": "number",
  "average_response_time": "number",
  "total_tokens_used": "number",
  "average_feedback_score": "number",
  "unique_users": "number"
}
```

## 🔄 Data Flow

### Event Ingestion Flow
1. **AI Agent** sends event data to `/api/v1/agents/{agent_id}/events`
2. **FastAPI Backend** validates data using Pydantic models
3. **Backend** stores raw event in DynamoDB Events table
4. **Backend** returns success response to agent

### Metrics Retrieval Flow
1. **Frontend Dashboard** requests metrics via `/api/v1/agents/{agent_id}/metrics`
2. **FastAPI Backend** queries DynamoDB Metrics table
3. **Backend** aggregates data if needed
4. **Backend** returns formatted metrics to frontend
5. **Frontend** renders charts and displays data

### Real-time Updates
- Frontend polls API endpoints every 30 seconds
- WebSocket support can be added for true real-time updates
- Dashboard automatically refreshes when agent selection changes

## 🐳 Deployment Architecture

### Docker Compose (Development)
```yaml
services:
  dynamodb-local:    # Local database
  backend:           # FastAPI application
  frontend:          # React application
```

### Production Deployment
```yaml
services:
  dynamodb:          # AWS DynamoDB
  backend:           # FastAPI + Gunicorn
  frontend:          # Nginx + React build
  load-balancer:     # Nginx reverse proxy
```

## 🔒 Security Considerations

### API Security
- CORS configuration for cross-origin requests
- Input validation using Pydantic models
- Rate limiting (can be implemented)
- API key authentication (recommended for production)

### Data Security
- Environment variables for sensitive configuration
- No hardcoded credentials
- DynamoDB access controlled via IAM roles
- Data encryption at rest and in transit

### Frontend Security
- HTTPS enforcement in production
- Content Security Policy headers
- XSS protection via React's built-in escaping
- CSRF protection via same-origin policy

## 📈 Scalability Design

### Horizontal Scaling
- **Backend**: Multiple FastAPI instances behind load balancer
- **Database**: DynamoDB's built-in scaling capabilities
- **Frontend**: Static file serving via CDN

### Performance Optimizations
- **Caching**: API response caching with Redis (future enhancement)
- **Pagination**: Large dataset handling with pagination
- **Compression**: Gzip compression for API responses
- **Database Indexes**: Optimized DynamoDB queries

### Monitoring & Observability
- **Health Checks**: `/health` endpoint for service monitoring
- **Metrics**: Application performance monitoring
- **Logging**: Structured logging with correlation IDs
- **Alerts**: Error rate and performance threshold alerts

## 🔧 Configuration Management

### Environment Variables
```bash
# Backend
AWS_REGION=us-east-1
DYNAMODB_TABLE_EVENTS=ai-agent-events
DYNAMODB_TABLE_METRICS=ai-agent-metrics
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Frontend
REACT_APP_API_URL=http://localhost:8001/api/v1
```

### Configuration Files
- `backend/config.py`: Backend configuration
- `frontend/package.json`: Frontend dependencies
- `docker-compose.yml`: Service orchestration
- `nginx.conf`: Production web server config

## 🚀 Future Enhancements

### Planned Features
- **WebSocket Support**: Real-time dashboard updates
- **Advanced Analytics**: Machine learning insights
- **Custom Dashboards**: User-configurable views
- **Alert System**: Email/Slack notifications
- **Export Features**: CSV/PDF report generation

### Architectural Improvements
- **Microservices Split**: Separate services for different domains
- **Event-Driven Architecture**: Kafka for event streaming
- **GraphQL API**: More flexible data querying
- **Multi-Region Support**: Global deployment capabilities

## 📊 Monitoring & Analytics

### Application Metrics
- API response times
- Error rates by endpoint
- Database query performance
- Frontend load times

### Business Metrics
- Active agents count
- Total messages processed
- User engagement scores
- System uptime

This architecture provides a solid foundation for monitoring AI agent performance while maintaining scalability, security, and maintainability.