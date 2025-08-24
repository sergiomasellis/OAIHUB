#!/usr/bin/env python3
"""
Populate Sample Data for Local Development
This script populates DynamoDB with sample data for local development testing.
"""

import boto3
import time
import requests
import os
from datetime import datetime, timedelta

# Configuration
DYNAMODB_ENDPOINT = "http://localhost:8000"
DYNAMODB_TABLE_EVENTS = "ai-agent-events"
DYNAMODB_TABLE_METRICS = "ai-agent-metrics"
AWS_REGION = "us-east-1"

def wait_for_services():
    """Wait for required services to be available"""
    print("⏳ Waiting for services to be ready...")

    # Wait for DynamoDB Local
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(DYNAMODB_ENDPOINT, timeout=5)
            if response.status_code == 400:  # DynamoDB Local returns 400 for invalid requests
                print("✅ DynamoDB Local is ready")
                break
        except requests.exceptions.RequestException:
            pass

        if attempt == max_attempts - 1:
            print("❌ DynamoDB Local not ready after 30 seconds")
            return False

        print(f"⏳ Waiting for DynamoDB Local... ({attempt + 1}/{max_attempts})")
        time.sleep(1)

    # Wait for Backend API
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend API is ready")
                break
        except requests.exceptions.RequestException:
            pass

        if attempt == max_attempts - 1:
            print("❌ Backend API not ready after 30 seconds")
            return False

        print(f"⏳ Waiting for Backend API... ({attempt + 1}/{max_attempts})")
        time.sleep(1)

    return True

def create_dynamodb_tables():
    """Create DynamoDB tables for AI agent tracking"""
    print("🔧 Creating DynamoDB tables...")

    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        endpoint_url=DYNAMODB_ENDPOINT,
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
        print(f"✅ Created table: {DYNAMODB_TABLE_EVENTS}")
    except Exception as e:
        print(f"⚠️  Table {DYNAMODB_TABLE_EVENTS} might already exist: {e}")

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
        print(f"✅ Created table: {DYNAMODB_TABLE_METRICS}")
    except Exception as e:
        print(f"⚠️  Table {DYNAMODB_TABLE_METRICS} might already exist: {e}")

def populate_sample_data():
    """Populate DynamoDB with sample metrics data for demo purposes"""
    print("📊 Populating sample data...")

    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        endpoint_url=DYNAMODB_ENDPOINT,
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
            'feedback_count': 145
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
            'feedback_count': 175
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
            'feedback_count': 118
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
            'feedback_count': 215
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
            'feedback_count': 245
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
            'feedback_count': 177
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
            'feedback_count': 196
        }
    ]

    for item in sample_data:
        try:
            metrics_table.put_item(Item=item)
            print(f"✅ Added sample data for {item['agent_id']} on {item['date']}")
        except Exception as e:
            print(f"❌ Error adding sample data: {e}")

    print("✅ Sample metrics data population completed!")

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
            print(f"✅ Added sample event for {event['agent_id']}")
        except Exception as e:
            print(f"❌ Error adding sample event: {e}")

    print("✅ Sample events data population completed!")

def main():
    """Main function to setup local development data"""
    print("🚀 Setting up local development data...")
    print("=" * 50)

    if not wait_for_services():
        print("❌ Services not ready. Please ensure docker-compose is running.")
        return 1

    create_dynamodb_tables()
    populate_sample_data()

    print("=" * 50)
    print("✅ Local development data setup complete!")
    print("")
    print("📊 Your dashboard should now show:")
    print("   • KPI Metrics with realistic values")
    print("   • Time series charts with visitor data")
    print("   • Agent filtering (agent-1, agent-2)")
    print("   • Date range: July 25 - Aug 24, 2025")
    print("")
    print("🌐 Access your dashboard at: http://localhost:3000")
    print("")
    print("🔄 To reset data:")
    print("   docker-compose down && docker-compose up -d")
    print("   python scripts/populate_sample_data.py")

    return 0

if __name__ == "__main__":
    exit(main())