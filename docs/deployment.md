# Deployment Guide

Complete deployment instructions for the AI Agent Tracking Dashboard in various environments.

## 🚀 Quick Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd ai-agent-tracking-dashboard

# Start all services
docker-compose up --build

# Access dashboard at http://localhost:3000
```

### Option 2: Manual Deployment

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm start
```

### Option 3: Cloud Deployment

- **AWS**: ECS + Fargate + DynamoDB
- **Google Cloud**: Cloud Run + Firestore
- **Azure**: Container Instances + CosmosDB

## 🐳 Docker Deployment

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  dynamodb-local:
    image: amazon/dynamodb-local
    ports:
      - "8000:8000"
    command: ["-jar", "DynamoDBLocal.jar", "-sharedDb", "-inMemory"]
    volumes:
      - dynamodb-data:/home/dynamodblocal/data

  backend:
    build: ./backend
    ports:
      - "8001:8000"
    environment:
      - AWS_REGION=us-east-1
      - DYNAMODB_TABLE_EVENTS=ai-agent-events
      - DYNAMODB_TABLE_METRICS=ai-agent-metrics
    depends_on:
      - dynamodb-local
    volumes:
      - ./backend:/app
    command: ["python", "main.py"]

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8001/api/v1

volumes:
  dynamodb-data:
```

### Building Custom Images

#### Backend Image
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

#### Frontend Image
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Multi-Stage Build Optimization

```dockerfile
# Backend multi-stage build
FROM python:3.13-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.13-slim as runtime

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

CMD ["python", "main.py"]
```

## ☁️ Cloud Deployments

### AWS Deployment

#### 1. DynamoDB Setup
```bash
# Create DynamoDB tables
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

#### 2. ECS Fargate Deployment
```yaml
# Task Definition
{
  "family": "ai-agent-tracking-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-agent-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "DYNAMODB_TABLE_EVENTS",
          "value": "ai-agent-events"
        },
        {
          "name": "DYNAMODB_TABLE_METRICS",
          "value": "ai-agent-metrics"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-agent-tracking-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Application Load Balancer
```hcl
# Terraform example
resource "aws_lb" "main" {
  name               = "ai-agent-tracking-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets           = aws_subnet.public.*.id

  enable_deletion_protection = false
}

resource "aws_lb_target_group" "backend" {
  name        = "ai-agent-tracking-backend"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path = "/health"
    port = "8000"
  }
}
```

### Google Cloud Platform

#### 1. Firestore Setup
```bash
# Create Firestore database
gcloud firestore databases create --region=us-central1

# Create indexes (if needed)
# Firestore automatically creates single-field indexes
```

#### 2. Cloud Run Deployment
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-agent-backend', './backend']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-agent-backend']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'ai-agent-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ai-agent-backend'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

### Azure Deployment

#### 1. CosmosDB Setup
```bash
# Create CosmosDB account
az cosmosdb create \
  --name ai-agent-tracking-db \
  --resource-group myResourceGroup \
  --kind GlobalDocumentDB \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=false

# Create database and containers
az cosmosdb sql database create \
  --account-name ai-agent-tracking-db \
  --name ai-agent-tracking \
  --resource-group myResourceGroup

az cosmosdb sql container create \
  --account-name ai-agent-tracking-db \
  --database-name ai-agent-tracking \
  --name events \
  --partition-key-path "/agent_id" \
  --resource-group myResourceGroup

az cosmosdb sql container create \
  --account-name ai-agent-tracking-db \
  --database-name ai-agent-tracking \
  --name metrics \
  --partition-key-path "/agent_id" \
  --resource-group myResourceGroup
```

#### 2. Container Instances Deployment
```json
{
  "location": "East US",
  "properties": {
    "containers": [
      {
        "name": "ai-agent-backend",
        "properties": {
          "image": "your-registry.azurecr.io/ai-agent-backend:latest",
          "ports": [
            {
              "port": 8000
            }
          ],
          "environmentVariables": [
            {
              "name": "COSMOSDB_ENDPOINT",
              "value": "https://ai-agent-tracking-db.documents.azure.com:443/"
            },
            {
              "name": "COSMOSDB_KEY",
              "value": "your-cosmosdb-key"
            }
          ],
          "resources": {
            "requests": {
              "cpu": 1,
              "memoryInGB": 1.5
            }
          }
        }
      }
    ],
    "osType": "Linux",
    "restartPolicy": "Always",
    "ipAddress": {
      "type": "Public",
      "ports": [
        {
          "protocol": "TCP",
          "port": 8000
        }
      ]
    }
  }
}
```

## 🏢 Enterprise Deployment

### High Availability Setup

#### Load Balancer Configuration
```nginx
# nginx.conf for load balancing
upstream backend_servers {
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}

server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### Database Replication
```sql
-- PostgreSQL example (if using PostgreSQL instead of DynamoDB)
-- Create read replicas
CREATE PUBLICATION events_pub FOR TABLE agent_events;
CREATE PUBLICATION metrics_pub FOR TABLE agent_metrics;

-- On replica
CREATE SUBSCRIPTION events_sub
    CONNECTION 'host=primary.example.com port=5432 user=replicator dbname=ai_agent_tracking'
    PUBLICATION events_pub;

CREATE SUBSCRIPTION metrics_sub
    CONNECTION 'host=primary.example.com port=5432 user=replicator dbname=ai_agent_tracking'
    PUBLICATION metrics_pub;
```

### Security Configuration

#### SSL/TLS Setup
```nginx
# nginx.conf with SSL
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://backend_servers;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

#### API Gateway Configuration
```yaml
# AWS API Gateway
openapi: 3.0.1
info:
  title: AI Agent Tracking API
  version: v1
paths:
  /api/v1/agents/{agent_id}/events:
    post:
      summary: Record agent event
      security:
        - apiKey: []
      parameters:
        - name: agent_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AgentEvent'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentEventResponse'

components:
  securitySchemes:
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
  schemas:
    AgentEvent:
      type: object
      required:
        - agent_id
        - timestamp
        - message_type
      properties:
        agent_id:
          type: string
        timestamp:
          type: string
          format: date-time
        message_type:
          type: string
          enum: [user_message, agent_response, error, feedback]
        content:
          type: string
        metadata:
          type: object
        response_time_ms:
          type: integer
        token_count:
          type: integer
        model_used:
          type: string
        user_feedback:
          type: integer
          minimum: 1
          maximum: 5
```

## 📊 Monitoring & Observability

### Application Monitoring

#### Health Checks
```python
# backend/main.py
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {
            "database": await check_database_health(),
            "memory": get_memory_usage(),
            "disk": get_disk_usage()
        }
    }
    return health_status

async def check_database_health():
    """Check database connectivity"""
    try:
        # Test database connection
        dynamodb = get_dynamodb_client()
        dynamodb.list_tables()
        return {"status": "healthy", "response_time_ms": 100}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### Metrics Collection
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

@app.middleware("http")
async def add_prometheus_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    request_duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(request_duration)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration

#### Structured Logging
```python
# logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON formatter for production
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for production
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Usage in main.py
logger = setup_logging()

@app.post("/api/v1/agents/{agent_id}/events")
async def record_agent_event(agent_id: str, event: AgentEvent):
    logger.info(
        "Recording agent event",
        extra={
            "agent_id": agent_id,
            "message_type": event.message_type,
            "timestamp": event.timestamp
        }
    )
    # ... rest of the function
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python -m pytest

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Build and push backend image
        run: |
          cd backend
          docker build -t ai-agent-backend .
          docker tag ai-agent-backend:latest ${{ secrets.ECR_REGISTRY }}/ai-agent-backend:latest
          docker push ${{ secrets.ECR_REGISTRY }}/ai-agent-backend:latest

      - name: Build and push frontend image
        run: |
          cd frontend
          docker build -t ai-agent-frontend .
          docker tag ai-agent-frontend:latest ${{ secrets.ECR_REGISTRY }}/ai-agent-frontend:latest
          docker push ${{ secrets.ECR_REGISTRY }}/ai-agent-frontend:latest

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ai-agent-tracking-cluster \
            --service ai-agent-tracking-service \
            --force-new-deployment
```

## 🚨 Backup & Recovery

### Database Backup

#### DynamoDB Backup
```bash
# Create backup
aws dynamodb create-backup \
  --table-name ai-agent-events \
  --backup-name ai-agent-events-backup-$(date +%Y%m%d-%H%M%S)

aws dynamodb create-backup \
  --table-name ai-agent-metrics \
  --backup-name ai-agent-metrics-backup-$(date +%Y%m%d-%H%M%S)

# List backups
aws dynamodb list-backups --table-name ai-agent-events

# Restore from backup
aws dynamodb restore-table-from-backup \
  --target-table-name ai-agent-events-restored \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/ai-agent-events/backup/12345678901234-abcd
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d-%H%M%S)
TABLES=("ai-agent-events" "ai-agent-metrics")

for table in "${TABLES[@]}"; do
    echo "Creating backup for $table"
    aws dynamodb create-backup \
      --table-name "$table" \
      --backup-name "${table}-backup-${DATE}"
done

# Clean up old backups (older than 30 days)
aws dynamodb list-backups --table-name ai-agent-events | \
  jq -r '.BackupSummaries[] | select(.BackupCreationDateTime < now - 2592000) | .BackupArn' | \
  xargs -I {} aws dynamodb delete-backup --backup-arn {}
```

## 📈 Performance Optimization

### Database Optimization

#### DynamoDB Best Practices
```python
# Optimized DynamoDB operations
def batch_write_events(events):
    """Batch write multiple events"""
    dynamodb = get_dynamodb_client()
    table = dynamodb.Table(Config.DYNAMODB_TABLE_EVENTS)

    with table.batch_writer() as batch:
        for event in events:
            batch.put_item(Item=event)

def query_with_pagination(agent_id, start_time, end_time):
    """Query with pagination to handle large datasets"""
    dynamodb = get_dynamodb_client()
    table = dynamodb.Table(Config.DYNAMODB_TABLE_EVENTS)

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id) &
                              boto3.dynamodb.conditions.Key('timestamp').between(start_time, end_time),
        ScanIndexForward=True,  # Sort by timestamp ascending
        Limit=1000
    )

    items = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id) &
                                  boto3.dynamodb.conditions.Key('timestamp').between(start_time, end_time),
            ExclusiveStartKey=response['LastEvaluatedKey'],
            ScanIndexForward=True,
            Limit=1000
        )
        items.extend(response['Items'])

    return items
```

### Caching Strategy

#### Redis Caching
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_metrics(agent_id, date):
    """Get metrics from cache"""
    cache_key = f"metrics:{agent_id}:{date}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)
    return None

def set_cached_metrics(agent_id, date, metrics):
    """Cache metrics data"""
    cache_key = f"metrics:{agent_id}:{date}"
    redis_client.setex(
        cache_key,
        3600,  # 1 hour expiry
        json.dumps(metrics)
    )
```

This comprehensive deployment guide covers everything needed to deploy the AI Agent Tracking Dashboard in various environments, from simple Docker setups to complex enterprise configurations.