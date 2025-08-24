import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE_EVENTS = os.getenv("DYNAMODB_TABLE_EVENTS", "ai-agent-events")
    DYNAMODB_TABLE_METRICS = os.getenv("DYNAMODB_TABLE_METRICS", "ai-agent-metrics")
    DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    # Search backend selection: 'dynamodb' (default) or 'opensearch'
    SEARCH_BACKEND = os.getenv("SEARCH_BACKEND", "dynamodb").lower()

    # OpenSearch config
    OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "")
    OPENSEARCH_USER = os.getenv("OPENSEARCH_USER", "")
    OPENSEARCH_PASS = os.getenv("OPENSEARCH_PASS", "")
    OPENSEARCH_INDEX_EVENTS = os.getenv("OPENSEARCH_INDEX_EVENTS", "events-v1")
    OPENSEARCH_INDEX_SPANS = os.getenv("OPENSEARCH_INDEX_SPANS", "spans-v1")
