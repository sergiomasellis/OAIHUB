import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Agent Tracking API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_agents():
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    # This will return empty list initially since no data is set up
    assert isinstance(response.json(), list)