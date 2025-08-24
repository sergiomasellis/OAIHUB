# Troubleshooting Guide

Common issues and solutions for the AI Agent Tracking Dashboard.

## 🚨 Quick Issue Resolution

### Dashboard Not Loading
```bash
# Check if services are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Check frontend logs
docker-compose logs frontend

# Restart services
docker-compose restart
```

### API Not Responding
```bash
# Test backend health
curl http://localhost:8001/health

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

## 🔧 Common Issues

### 1. Docker Issues

#### Problem: Docker containers fail to start
**Symptoms:**
- `docker-compose up` fails
- Port binding errors
- Container exits immediately

**Solutions:**
```bash
# Clean up Docker resources
docker-compose down
docker system prune -a
docker volume prune

# Rebuild without cache
docker-compose build --no-cache
docker-compose up --build

# Check available disk space
df -h

# Check Docker daemon status
sudo systemctl status docker
```

#### Problem: Port conflicts
**Symptoms:**
- "Port is already allocated" error
- Services can't bind to ports

**Solutions:**
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8001
lsof -i :8000

# Kill processes using the ports
kill -9 <PID>

# Or use different ports in docker-compose.yml
# Change ports section to:
# ports:
#   - "3001:80"  # Frontend
#   - "8002:8000"  # Backend
#   - "8001:8000"  # DynamoDB
```

#### Problem: Docker build fails
**Symptoms:**
- Build process stops with errors
- Missing dependencies

**Solutions:**
```bash
# Update Docker and Docker Compose
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Check Docker version
docker --version
docker-compose --version

# Build with verbose output
docker-compose build --progress=plain

# Clean build cache
docker builder prune -a
```

### 2. Backend Issues

#### Problem: Python dependency conflicts
**Symptoms:**
- Import errors for FastAPI, pydantic
- Python version compatibility issues

**Solutions:**
```bash
# Check Python version
python3 --version

# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install compatible versions
pip install fastapi==0.95.2 uvicorn==0.20.0 pydantic==1.10.22

# Or use requirements.txt
pip install -r requirements.txt
```

#### Problem: Database connection errors
**Symptoms:**
- "Unable to connect to DynamoDB" errors
- Timeout errors when accessing database

**Solutions:**
```bash
# Check if DynamoDB Local is running
curl http://localhost:8000/

# Restart DynamoDB container
docker-compose restart dynamodb-local

# Check backend environment variables
cd backend
cat .env

# Verify table creation
python ../infrastructure/setup_dynamodb.py
```

#### Problem: CORS errors
**Symptoms:**
- Frontend can't communicate with backend
- "CORS error" in browser console

**Solutions:**
```python
# Update CORS settings in backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Frontend Issues

#### Problem: React app not starting
**Symptoms:**
- "Failed to compile" errors
- Module not found errors
- Port already in use

**Solutions:**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force

# Use different port
PORT=3001 npm start

# Check for conflicting processes
lsof -i :3000
```

#### Problem: API calls failing
**Symptoms:**
- "Network Error" in browser console
- 404 or 500 errors from API calls

**Solutions:**
```bash
# Check if backend is running
curl http://localhost:8001/health

# Verify API URL in frontend
cd frontend
grep REACT_APP_API_URL .env

# Check browser network tab for exact error
# Look for CORS headers in response
```

### 4. Database Issues

#### Problem: DynamoDB Local not persisting data
**Symptoms:**
- Data disappears after container restart
- Tables not found after restart

**Solutions:**
```bash
# Use persistent volume in docker-compose.yml
services:
  dynamodb-local:
    volumes:
      - dynamodb-data:/home/dynamodblocal/data

volumes:
  dynamodb-data:

# Or use in-memory mode for development
command: ["-jar", "DynamoDBLocal.jar", "-sharedDb", "-inMemory"]
```

#### Problem: Table creation fails
**Symptoms:**
- "Table already exists" errors
- Permission errors

**Solutions:**
```bash
# Delete existing tables
aws dynamodb delete-table --table-name ai-agent-events
aws dynamodb delete-table --table-name ai-agent-metrics

# Or use different table names in .env
DYNAMODB_TABLE_EVENTS=ai-agent-events-dev
DYNAMODB_TABLE_METRICS=ai-agent-metrics-dev
```

### 5. Integration Issues

#### Problem: LangChain integration not working
**Symptoms:**
- Events not being tracked
- Import errors with tracking handler

**Solutions:**
```python
# Check LangChain version compatibility
pip show langchain

# Update to compatible version
pip install langchain==0.0.300

# Verify tracking handler implementation
from langchain.callbacks.base import BaseCallbackHandler

class AgentTrackingHandler(BaseCallbackHandler):
    # Ensure all required methods are implemented
    def on_llm_start(self, serialized, prompts, **kwargs):
        pass

    def on_llm_end(self, response, **kwargs):
        pass

    def on_llm_error(self, error, **kwargs):
        pass
```

#### Problem: OpenAI API integration issues
**Symptoms:**
- Token counting errors
- Model name not recognized

**Solutions:**
```python
# Check OpenAI package version
pip show openai

# Update to latest version
pip install openai==1.3.0

# Handle different response formats
def extract_token_count(response):
    """Extract token count from different OpenAI response formats"""
    if hasattr(response, 'usage'):
        return response.usage.total_tokens
    elif 'usage' in response:
        return response['usage']['total_tokens']
    return 0
```

## 🔍 Debugging Tools

### Backend Debugging

#### Enable Debug Mode
```python
# Add to backend/main.py
import logging

logging.basicConfig(level=logging.DEBUG)

# Or use uvicorn with debug
uvicorn.run(app, host="0.0.0.0", port=8000, debug=True, reload=True)
```

#### API Testing
```bash
# Test health endpoint
curl http://localhost:8001/health

# Test API endpoints
curl -X POST http://localhost:8001/api/v1/agents/test-agent/events \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent",
    "timestamp": "2024-01-07T10:00:00Z",
    "message_type": "user_message",
    "content": "Test message"
  }'

# Test metrics endpoint
curl "http://localhost:8001/api/v1/agents/test-agent/metrics?days=1"
```

### Frontend Debugging

#### Browser Developer Tools
1. Open browser DevTools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for API requests
4. Check Application tab for local storage

#### React Development Tools
```bash
# Install React DevTools browser extension
# Chrome: https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/react-devtools/
```

#### Debug API Calls
```javascript
// Add logging to API service
export const apiService = {
  async getAgentMetrics(agentId, days = 7) {
    console.log('Fetching metrics for:', agentId);
    try {
      const response = await api.get(`/agents/${agentId}/metrics`, {
        params: { days }
      });
      console.log('Metrics response:', response.data);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};
```

### Database Debugging

#### DynamoDB Local Web Interface
```bash
# Access DynamoDB Local web interface
open http://localhost:8000/shell/

# Or use AWS CLI
aws dynamodb list-tables --endpoint-url http://localhost:8000

aws dynamodb scan --table-name ai-agent-events --endpoint-url http://localhost:8000
```

#### Query Debugging
```python
# Add debug logging to database operations
import logging

logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger('boto3.resources', logging.DEBUG)
boto3.set_stream_logger('botocore', logging.DEBUG)
```

## 📊 Performance Issues

### Slow API Responses

#### Problem: High latency on API calls
**Solutions:**
```python
# Add response time logging
@app.middleware("http")
async def log_request_time(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.method} {request.url} - Time: {process_time:.3f}s")
    return response
```

#### Problem: Database query performance
**Solutions:**
```python
# Add query optimization
def optimized_query(agent_id, start_time, end_time):
    """Use query instead of scan for better performance"""
    table = dynamodb.Table('ai-agent-events')

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id) &
                              boto3.dynamodb.conditions.Key('timestamp').between(start_time, end_time),
        IndexName='MessageTypeIndex'  # Use GSI if appropriate
    )

    return response['Items']
```

### Memory Issues

#### Problem: High memory usage
**Solutions:**
```python
# Monitor memory usage
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")

# Add to periodic tasks
import asyncio

async def monitor_resources():
    while True:
        log_memory_usage()
        await asyncio.sleep(60)  # Log every minute
```

### Frontend Performance

#### Problem: Slow dashboard loading
**Solutions:**
```javascript
// Implement lazy loading
const MetricsChart = React.lazy(() => import('./components/MetricsChart'));

function Dashboard() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <MetricsChart />
    </React.Suspense>
  );
}

// Add service worker for caching
// Create src/serviceWorker.js and register it
```

## 🔒 Security Issues

### API Security

#### Problem: Unauthorized access
**Solutions:**
```python
# Add API key authentication
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()

async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

@app.post("/api/v1/agents/{agent_id}/events")
async def record_agent_event(
    agent_id: str,
    event: AgentEvent,
    api_key: str = Depends(get_api_key)
):
    # Your endpoint logic here
    pass
```

#### Problem: CORS configuration issues
**Solutions:**
```python
# Restrict CORS origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-dashboard-domain.com",
        "https://your-api-domain.com"
    ],  # Replace with your actual domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📝 Logging and Monitoring

### Enhanced Logging

#### Problem: Insufficient logging
**Solutions:**
```python
# Add structured logging
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use in endpoints
@app.post("/api/v1/agents/{agent_id}/events")
async def record_agent_event(agent_id: str, event: AgentEvent):
    logger.info(f"Recording event for agent {agent_id}", extra={
        'agent_id': agent_id,
        'message_type': event.message_type,
        'timestamp': event.timestamp
    })
    # Your logic here
```

### Error Tracking

#### Problem: Unhandled errors
**Solutions:**
```python
# Add global exception handler
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(f"Request completed", extra={
        'method': request.method,
        'url': str(request.url),
        'status_code': response.status_code,
        'process_time': process_time
    })

    return response
```

## 🚀 Getting Help

If you can't resolve an issue using this guide:

1. **Check GitHub Issues**: Search existing issues or create a new one
2. **Provide Debug Information**:
   - Docker logs: `docker-compose logs`
   - Error messages and stack traces
   - System information: `uname -a`, `python --version`, `node --version`
   - Configuration files (without sensitive data)
3. **Test with Minimal Setup**: Try reproducing the issue with a minimal configuration
4. **Check Dependencies**: Verify all required packages are installed and compatible

## 📋 Quick Reference

### Essential Commands
```bash
# Start services
docker-compose up --build

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Clean up
docker-compose down
docker system prune -a

# Backend testing
cd backend && source venv/bin/activate
python main.py

# Frontend testing
cd frontend && npm start
```

### Health Check Endpoints
- Backend: `http://localhost:8001/health`
- Frontend: `http://localhost:3000` (check if loads)
- DynamoDB: `http://localhost:8000/` (should return XML)

### Common Error Codes
- `400`: Bad Request - Check request format
- `401`: Unauthorized - Check API keys
- `404`: Not Found - Check URLs and agent IDs
- `500`: Internal Error - Check logs for details

This troubleshooting guide should help resolve most common issues. For complex problems, consider reaching out to the community or opening an issue with detailed information.