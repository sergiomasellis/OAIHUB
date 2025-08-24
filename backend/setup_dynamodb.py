import boto3
import os

# Configuration - using same defaults as config.py
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_EVENTS = os.getenv("DYNAMODB_TABLE_EVENTS", "ai-agent-events")
DYNAMODB_TABLE_METRICS = os.getenv("DYNAMODB_TABLE_METRICS", "ai-agent-metrics")

def create_dynamodb_tables():
    """Create DynamoDB tables for AI agent tracking"""

    # For local development, use DynamoDB Local
    # In production, this would use AWS DynamoDB
    dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        endpoint_url=dynamodb_endpoint,
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )

    # Create table for raw events
    try:
        events_table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_EVENTS,
            KeySchema=[
                {
                    'AttributeName': 'agent_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'agent_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Add GSI for querying by message type
        events_table.update(
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'MessageTypeIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'message_type',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ]
        )

        print(f"Created table: {DYNAMODB_TABLE_EVENTS}")

    except Exception as e:
        print(f"Table {DYNAMODB_TABLE_EVENTS} might already exist: {e}")

    # Create table for aggregated metrics
    try:
        metrics_table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_METRICS,
            KeySchema=[
                {
                    'AttributeName': 'agent_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'date',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'agent_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        print(f"Created table: {DYNAMODB_TABLE_METRICS}")

    except Exception as e:
        print(f"Table {DYNAMODB_TABLE_METRICS} might already exist: {e}")

def populate_sample_data():
    """Populate DynamoDB with sample metrics data for demo purposes"""
    dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        endpoint_url=dynamodb_endpoint,
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )

    metrics_table = dynamodb.Table(DYNAMODB_TABLE_METRICS)

    # Sample data for July-August 2025 (matching the date range user is querying)
    sample_data = [
        {
            'agent_id': 'agent-1',
            'date': '2025-07-25',
            'total_messages': 150,
            'total_responses': 145,
            'total_errors': 5,
            'total_tokens_used': 12500,
            'unique_users': 45,
            'response_time_sum': 36000,  # 240ms average
            'response_count': 145,
            'feedback_sum': 680,  # 4.7 average
            'feedback_count': 145,
            'models': ['GPT-4o', 'GPT-3.5', 'o3-mini'],  # Models used by this agent
            'model_usage': {'GPT-4o': 120, 'GPT-3.5': 25, 'o3-mini': 5}  # Usage count per model
        },
        {
            'agent_id': 'agent-1',
            'date': '2025-07-26',
            'total_messages': 180,
            'total_responses': 175,
            'total_errors': 3,
            'total_tokens_used': 15800,
            'unique_users': 52,
            'response_time_sum': 42000,  # 240ms average
            'response_count': 175,
            'feedback_sum': 825,  # 4.7 average
            'feedback_count': 175,
            'models': ['GPT-4o', 'GPT-4.1', 'o3-mini'],  # Models used by this agent
            'model_usage': {'GPT-4o': 140, 'GPT-4.1': 30, 'o3-mini': 10}  # Usage count per model
        },
        {
            'agent_id': 'agent-1',
            'date': '2025-07-27',
            'total_messages': 200,
            'total_responses': 195,
            'total_errors': 2,
            'total_tokens_used': 18200,
            'unique_users': 58,
            'response_time_sum': 46800,  # 240ms average
            'response_count': 195,
            'feedback_sum': 920,  # 4.7 average
            'feedback_count': 195
        },
        {
            'agent_id': 'agent-2',
            'date': '2025-07-25',
            'total_messages': 120,
            'total_responses': 118,
            'total_errors': 2,
            'total_tokens_used': 8900,
            'unique_users': 35,
            'response_time_sum': 23600,  # 200ms average
            'response_count': 118,
            'feedback_sum': 530,  # 4.5 average
            'feedback_count': 118,
            'models': ['o3', 'o4-mini', 'GPT-3.5'],  # Models used by this agent
            'model_usage': {'o3': 80, 'o4-mini': 35, 'GPT-3.5': 5}  # Usage count per model
        },
        {
            'agent_id': 'agent-2',
            'date': '2025-07-26',
            'total_messages': 140,
            'total_responses': 137,
            'total_errors': 1,
            'total_tokens_used': 10200,
            'unique_users': 40,
            'response_time_sum': 27400,  # 200ms average
            'response_count': 137,
            'feedback_sum': 615,  # 4.5 average
            'feedback_count': 137
        },
        {
            'agent_id': 'agent-2',
            'date': '2025-07-27',
            'total_messages': 160,
            'total_responses': 157,
            'total_errors': 3,
            'total_tokens_used': 11800,
            'unique_users': 45,
            'response_time_sum': 31400,  # 200ms average
            'response_count': 157,
            'feedback_sum': 705,  # 4.5 average
            'feedback_count': 157
        },
        {
            'agent_id': 'agent-1',
            'date': '2025-08-20',
            'total_messages': 220,
            'total_responses': 215,
            'total_errors': 4,
            'total_tokens_used': 19500,
            'unique_users': 65,
            'response_time_sum': 51600,  # 240ms average
            'response_count': 215,
            'feedback_sum': 1015,  # 4.7 average
            'feedback_count': 215,
            'models': ['GPT-4o', 'GPT-4.1', 'o3-mini'],  # Models used by this agent
            'model_usage': {'GPT-4o': 180, 'GPT-4.1': 35, 'o3-mini': 5}  # Usage count per model
        },
        {
            'agent_id': 'agent-1',
            'date': '2025-08-21',
            'total_messages': 250,
            'total_responses': 245,
            'total_errors': 3,
            'total_tokens_used': 21800,
            'unique_users': 70,
            'response_time_sum': 58800,  # 240ms average
            'response_count': 245,
            'feedback_sum': 1155,  # 4.7 average
            'feedback_count': 245,
            'models': ['GPT-4o', 'GPT-4.1', 'o3-mini'],  # Models used by this agent
            'model_usage': {'GPT-4o': 200, 'GPT-4.1': 40, 'o3-mini': 10}  # Usage count per model
        },
        {
            'agent_id': 'agent-2',
            'date': '2025-08-20',
            'total_messages': 180,
            'total_responses': 177,
            'total_errors': 2,
            'total_tokens_used': 13200,
            'unique_users': 50,
            'response_time_sum': 35400,  # 200ms average
            'response_count': 177,
            'feedback_sum': 795,  # 4.5 average
            'feedback_count': 177,
            'models': ['o3', 'o4-mini', 'GPT-3.5'],  # Models used by this agent
            'model_usage': {'o3': 120, 'o4-mini': 50, 'GPT-3.5': 10}  # Usage count per model
        },
        {
            'agent_id': 'agent-2',
            'date': '2025-08-21',
            'total_messages': 200,
            'total_responses': 196,
            'total_errors': 1,
            'total_tokens_used': 14500,
            'unique_users': 55,
            'response_time_sum': 39200,  # 200ms average
            'response_count': 196,
            'feedback_sum': 880,  # 4.5 average
            'feedback_count': 196,
            'models': ['o3', 'o4-mini', 'GPT-3.5'],  # Models used by this agent
            'model_usage': {'o3': 140, 'o4-mini': 50, 'GPT-3.5': 10}  # Usage count per model
        }
    ]

    for item in sample_data:
        try:
            metrics_table.put_item(Item=item)
            print(f"Added sample data for {item['agent_id']} on {item['date']}")
        except Exception as e:
            print(f"Error adding sample data: {e}")

    print("Sample data population completed!")

    # Also populate some sample events for the agents endpoint
    events_table = dynamodb.Table(DYNAMODB_TABLE_EVENTS)

    sample_events = [
        {
            'agent_id': 'agent-1',
            'timestamp': '2025-08-20T10:00:00Z',
            'message_type': 'user_message',
            'content': 'Hello, can you help me?',
            'trace_id': 'trace-001',
            'conversation_id': 'conv-001',
            'model_used': 'gpt-4o',
            'token_count': 25
        },
        {
            'agent_id': 'agent-1',
            'timestamp': '2025-08-20T10:00:15Z',
            'message_type': 'agent_response',
            'content': 'Of course! I\'d be happy to help.',
            'trace_id': 'trace-001',
            'conversation_id': 'conv-001',
            'model_used': 'gpt-4o',
            'token_count': 45,
            'response_time_ms': 240
        },
        {
            'agent_id': 'agent-2',
            'timestamp': '2025-08-20T11:30:00Z',
            'message_type': 'user_message',
            'content': 'What\'s the weather like?',
            'trace_id': 'trace-002',
            'conversation_id': 'conv-002',
            'model_used': 'gpt-3.5-turbo',
            'token_count': 18
        },
        {
            'agent_id': 'agent-2',
            'timestamp': '2025-08-20T11:30:20Z',
            'message_type': 'agent_response',
            'content': 'I don\'t have access to current weather data.',
            'trace_id': 'trace-002',
            'conversation_id': 'conv-002',
            'model_used': 'gpt-3.5-turbo',
            'token_count': 32,
            'response_time_ms': 200
        }
    ]

    for event in sample_events:
        try:
            events_table.put_item(Item=event)
            print(f"Added sample event for {event['agent_id']}")
        except Exception as e:
            print(f"Error adding sample event: {e}")

    print("Sample events population completed!")

if __name__ == "__main__":
    create_dynamodb_tables()
    populate_sample_data()