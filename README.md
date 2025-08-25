# AI Agent Tracking Dashboard

A comprehensive monitoring and analytics platform for tracking AI agent performance, built with React, FastAPI, and DynamoDB.

<img width="1895" height="933" alt="image" src="https://github.com/user-attachments/assets/d1dfaf29-b27d-4d35-a61c-774964a7c405" />


## Architecture

- **Frontend**: React with TypeScript and Salt Design System
- **Backend**: FastAPI with Python
- **Database**: DynamoDB (local or AWS)
- **Charts**: Recharts for data visualization

## Features

- Real-time agent performance monitoring
- Interactive charts and metrics visualization
- Error tracking and analysis
- Response time monitoring
- Multi-agent support
- RESTful API for data ingestion

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository
2. Run the entire stack:
   ```bash
   docker-compose up --build
   ```

3. Access the dashboard at [http://localhost:3000](http://localhost:3000)

### Manual Setup

#### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up DynamoDB Local:
   ```bash
   docker run -p 8000:8000 amazon/dynamodb-local
   ```

5. Create tables:
   ```bash
   python ../infrastructure/setup_dynamodb.py
   ```

6. Start the backend:
   ```bash
   python main.py
   ```

#### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000)

## API Endpoints

- `GET /api/v1/agents` - List all agents
- `POST /api/v1/agents/{agent_id}/events` - Record agent event
- `GET /api/v1/agents/{agent_id}/metrics` - Get agent metrics

## Data Models

### Agent Event
```json
{
  "agent_id": "string",
  "timestamp": "string",
  "message_type": "user_message|agent_response|error|feedback",
  "content": "string",
  "response_time_ms": 0,
  "token_count": 0,
  "model_used": "string",
  "user_feedback": 1-5
}
```

### Agent Metrics
```json
{
  "agent_id": "string",
  "date": "string",
  "total_messages": 0,
  "total_responses": 0,
  "total_errors": 0,
  "average_response_time": 0.0,
  "total_tokens_used": 0,
  "average_feedback_score": 0.0,
  "unique_users": 0
}
```

## Environment Variables

### Backend (.env)
```env
AWS_REGION=us-east-1
DYNAMODB_TABLE_EVENTS=ai-agent-events
DYNAMODB_TABLE_METRICS=ai-agent-metrics
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8001/api/v1
```

## Development

### Running Tests

Backend:
```bash
cd backend
source venv/bin/activate
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Building for Production

Backend:
```bash
cd backend
docker build -t ai-agent-backend .
```

Frontend:
```bash
cd frontend
npm run build
docker build -t ai-agent-frontend .
```

## Deployment

The application can be deployed using the provided Docker Compose configuration or individual container deployments.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
