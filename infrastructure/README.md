# Infrastructure Setup

## DynamoDB Local Setup

For local development, we use DynamoDB Local to simulate AWS DynamoDB.

### Installation

1. Download DynamoDB Local:
   ```bash
   # Using Docker (recommended)
   docker run -p 8000:8000 amazon/dynamodb-local

   # Or download JAR file from AWS:
   # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
   ```

2. Set up tables:
   ```bash
   cd backend
   source venv/bin/activate
   python ../infrastructure/setup_dynamodb.py
   ```

### Tables Created

1. **ai-agent-events**: Stores raw event data
   - Partition key: `agent_id` (String)
   - Sort key: `timestamp` (String)
   - GSI: `MessageTypeIndex` for querying by message type

2. **ai-agent-metrics**: Stores aggregated metrics
   - Partition key: `agent_id` (String)
   - Sort key: `date` (String)

### Production Setup

For production, update the configuration to use actual AWS DynamoDB:
- Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`
- Remove the `endpoint_url` parameter from boto3 resource initialization
- Ensure proper IAM permissions for DynamoDB access