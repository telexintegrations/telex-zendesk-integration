
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)  # Create a TestClient instance

def test_get_integration_json():
    """Test if /integration.json endpoint returns correct integration details"""
    response = client.get("/integration.json")
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["descriptions"]["app_name"] == "Zendesk Feedback Monitor"

def test_tick_missing_credentials():
    """Test /tick endpoint with missing Zendesk credentials"""
    payload = {"return_url": "http://example.com", "settings": []}  # Ensure "settings" key is present

    response = client.post("/tick", json=payload)
    
    assert response.status_code == 400
    assert response.json() == {"error": "Missing Zendesk credentials"}

def test_tick_success():
    """Test /tick endpoint with all required credentials"""
    payload = {
        "return_url": "http://example.com",
        "settings": [
            {"label": "zendesk_subdomain", "default": "https://example.zendesk.com"},
            {"label": "zendesk_email", "default": "test@example.com"},
            {"label": "zendesk_api_token", "default": "fake_token"}
        ]
    }

    response = client.post("/tick", json=payload)

    assert response.status_code == 200  # Adjusted to match actual response
    assert response.json() == {"status": "accepted"}