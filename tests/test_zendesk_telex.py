import pytest
import httpx
from fastapi.testclient import TestClient
from main import app, send_feedback_to_telex
from services.zendesk import fetch_support_tickets, fetch_satisfaction_ratings

# Mock Zendesk API responses
def mock_zendesk_response(request: httpx.Request):
    if "tickets.json" in request.url.path:
        return httpx.Response(
            200,
            json={"tickets": [{"id": 1, "subject": "Test Ticket", "status": "open"}]},
        )
    if "satisfaction_ratings.json" in request.url.path:
        return httpx.Response(
            200,
            json={"satisfaction_ratings": [{"id": 101, "score": "good", "comment": "Great service!"}]},
        )
    return httpx.Response(404, json={"error": "Not found"})

@pytest.mark.asyncio
async def test_fetch_support_tickets():
    mock_transport = httpx.MockTransport(mock_zendesk_response)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        response = await fetch_support_tickets("zendesk_subdomain", "zendesk_email", "zendesk_api_token")
        assert isinstance(response, list)
        assert response[0]["id"] == 1

@pytest.mark.asyncio
async def test_fetch_satisfaction_ratings():
    mock_transport = httpx.MockTransport(mock_zendesk_response)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        response = await fetch_satisfaction_ratings("zendesk_subdomain", "zendesk_email", "zendesk_api_token")
        assert isinstance(response, list)
        assert response[0]["score"] == "good"

@pytest.mark.asyncio
async def test_send_feedback_to_telex():
    return_url = "https://ping.telex.im/v1/return/01952f76-98a2-7c94-86c4-2cfd787f36ec"
    zendesk_subdomain = "zendesk_subdomain"
    zendesk_email = "zendesk_email"
    zendesk_api_token = "zendesk_api_token"

    mock_transport = httpx.MockTransport(mock_zendesk_response)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        await send_feedback_to_telex(return_url, zendesk_subdomain, zendesk_email, zendesk_api_token)
        assert True  # Ensure no exceptions occur

client = TestClient(app)

def test_telex_tick():
    response = client.post(
        "/tick",
        json={
            "return_url": "https://ping.telex.im/v1/return/01952f76-98a2-7c94-86c4-2cfd787f36ec",
            "settings": [
                {"label": "zendesk_subdomain", "default": "zendesk_subdomain"},
                {"label": "zendesk_email", "default": "zendesk_email"},
                {"label": "zendesk_api_token", "default": "zendesk_api_token"},
            ],
        },
    )
    assert response.status_code == 202
