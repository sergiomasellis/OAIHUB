# Setup Guide

Complete installation and setup instructions for the AI Agent Tracking Dashboard.

## 🚀 Quick Start (Docker Compose)

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-tracking-dashboard

# Start all services
docker-compose up --build

# Access the dashboard
open http://localhost:3000
```

This will start:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **DynamoDB Local**: http://localhost:8000

## 📋 Prerequisites

### System Requirements
- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **Git**: For cloning the repository
- **Node.js**: Version 18+ (for manual frontend setup)
- **Python**: Version 3.8+ (for manual backend setup)

### Optional Requirements
- **AWS CLI**: For AWS DynamoDB integration
- **npm**: For frontend dependency management
- **pip**: For Python dependency management

## 🐳 Docker Setup (Recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-agent-tracking-dashboard
```

### 2. Environment Configuration
Create environment files for configuration:

**Backend (.env)**
```bash
cd backend
cat > .env << EOF
AWS_REGION=us-east-1
DYNAMODB_TABLE_EVENTS=ai-agent-events
DYNAMODB_TABLE_METRICS=ai-agent-metrics
EOF
```

**Frontend (.env)**
```bash
cd frontend
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8001/api/v1
EOF
```

### 3. Start Services
```bash
# From the project root
docker-compose up --build
```

### 4. Verify Installation
```bash
# Check if services are running
docker-compose ps

# Check backend health
curl http://localhost:8001/health

# Check frontend
curl http://localhost:3000
```

### 5. Initialize Database
```bash
# Run DynamoDB setup script
docker-compose exec backend python ../infrastructure/setup_dynamodb.py
```

## 🔧 Manual Setup

### Backend Setup

#### 1. Python Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### 2. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# If installation fails due to Python 3.13 compatibility:
pip install fastapi==0.95.2 uvicorn==0.20.0 pydantic==1.10.22 --force-reinstall
```

#### 3. DynamoDB Local Setup
```bash
# Start DynamoDB Local
docker run -p 8000:8000 amazon/dynamodb-local

# Or download and run manually:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
```

#### 4. Initialize Database
```bash
# Create DynamoDB tables
python ../infrastructure/setup_dynamodb.py
```

#### 5. Start Backend Server
```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

#### 1. Node.js Environment
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# If you encounter dependency issues:
npm install --legacy-peer-deps
```

#### 2. Environment Configuration
```bash
# Create environment file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8001/api/v1
EOF
```

#### 3. Start Development Server
```bash
# Start the development server
npm start

# The app will open at http://localhost:3000
```

## ☁️ AWS DynamoDB Setup (Production)

### 1. AWS Configuration
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. Create DynamoDB Tables
```bash
# Using AWS CLI
aws dynamodb create-table \
  --table-name ai-agent-events \
  --attribute-definitions \
    AttributeName=agent_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
    AttributeName=message_type,AttributeType=S \
  --key-schema \
    AttributeName=agent_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --global-secondary-indexes \
    '[
      {
        "IndexName": "MessageTypeIndex",
        "KeySchema": [
          {"AttributeName": "message_type", "KeyType": "HASH"},
          {"AttributeName": "timestamp", "KeyType": "RANGE"}
        ],
        "Projection": {"ProjectionType": "ALL"},
        "ProvisionedThroughput": {
          "ReadCapacityUnits": 5,
          "WriteCapacityUnits": 5
        }
      }
    ]' \
  --provisioned-throughput \
    ReadCapacityUnits=5,WriteCapacityUnits=5

# Create metrics table
aws dynamodb create-table \
  --table-name ai-agent-metrics \
  --attribute-definitions \
    AttributeName=agent_id,AttributeType=S \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=agent_id,KeyType=HASH \
    AttributeName=date,KeyType=RANGE \
  --provisioned-throughput \
    ReadCapacityUnits=5,WriteCapacityUnits=5
```

### 3. Update Backend Configuration
```bash
# Update backend/.env
cat > backend/.env << EOF
AWS_REGION=us-east-1
DYNAMODB_TABLE_EVENTS=ai-agent-events
DYNAMODB_TABLE_METRICS=ai-agent-metrics
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
EOF
```

## 🔍 Verification Steps

### 1. Backend Verification
```bash
# Test health endpoint
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy"}

# Test API endpoints
curl http://localhost:8001/api/v1/agents

# Expected response:
# []
```

### 2. Frontend Verification
```bash
# Open browser to http://localhost:3000
# You should see the dashboard with:
# - AI Agent Tracking Dashboard header
# - Agent selector (empty initially)
# - Metrics cards showing zeros
```

### 3. Database Verification
```bash
# Check DynamoDB tables
aws dynamodb list-tables --endpoint-url http://localhost:8000

# Expected output:
# {
#   "TableNames": [
#     "ai-agent-events",
#     "ai-agent-metrics"
#   ]
# }
```

## 🐛 Troubleshooting Setup Issues

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8001
lsof -i :8000

# Kill processes if needed
kill -9 <PID>
```

#### 2. Docker Issues
```bash
# Clean up Docker
docker-compose down
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 3. Python Dependency Issues
```bash
# Clear pip cache
pip cache purge

# Reinstall in clean environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 5. Database Connection Issues
```bash
# Test DynamoDB Local connection
curl http://localhost:8000/

# Check backend logs
docker-compose logs backend

# Verify environment variables
cat backend/.env
```

## 📊 Sample Data Setup

### Add Sample Agent Data
```bash
# Create sample events
curl -X POST http://localhost:8001/api/v1/agents/sample-agent/events \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "sample-agent",
    "timestamp": "2024-01-07T10:00:00Z",
    "message_type": "user_message",
    "content": "Hello, can you help me?",
    "metadata": {"user_id": "user-1"}
  }'

curl -X POST http://localhost:8001/api/v1/agents/sample-agent/events \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "sample-agent",
    "timestamp": "2024-01-07T10:00:05Z",
    "message_type": "agent_response",
    "content": "Of course! How can I assist you today?",
    "response_time_ms": 5000,
    "token_count": 25,
    "model_used": "gpt-4"
  }'
```

### Verify Sample Data
```bash
# Check agents list
curl http://localhost:8001/api/v1/agents

# Get metrics
curl "http://localhost:8001/api/v1/agents/sample-agent/metrics?days=1"
```

## 🔄 Updating the System

### Update Docker Images
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build
```

### Update Manual Installation
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update
```

## 🚀 Production Deployment

For production deployment, see the [Deployment Guide](./deployment.md) for detailed instructions on setting up the system in a production environment.

## 📞 Getting Help

If you encounter issues during setup:

1. Check the [Troubleshooting Guide](./troubleshooting.md)
2. Verify all prerequisites are met
3. Check Docker and service logs
4. Review environment configuration
5. Test individual components separately

For additional support, please check the project's issue tracker or documentation.