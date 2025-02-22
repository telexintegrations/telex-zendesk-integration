import httpx
import os
from config import ZENDESK_URL, ZENDESK_EMAIL, ZENDESK_API_TOKEN

AUTH = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

async def fetch_support_tickets():
    """Fetches support tickets from Zendesk."""
    zendesk_api_url = f"{ZENDESK_URL}/api/v2/tickets.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(zendesk_api_url, auth=AUTH)

        if response.status_code == 200:
            tickets = response.json().get("tickets", [])
            return [{"id": t["id"], "subject": t["subject"], "status": t["status"]} for t in tickets]
        
        return {"error": f"Failed to fetch tickets. Status: {response.status_code}"}

async def fetch_satisfaction_ratings():
    """Fetches customer satisfaction ratings from Zendesk."""
    url = f"{ZENDESK_URL}/api/v2/satisfaction_ratings.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, auth=AUTH)

        if response.status_code == 200:
            data = response.json()
            return [{"id": r["id"], "score": r["score"], "comment": r.get("comment", "No comment")} for r in data.get("satisfaction_ratings", [])]
        
        return {"error": f"Failed to fetch ratings. Status: {response.status_code}"}

async def fetch_ticket_metrics(ticket_id):
    """Fetches metrics for a specific ticket."""
    metrics_url = f"{ZENDESK_URL}/api/v2/tickets/{ticket_id}/metrics.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(metrics_url, auth=AUTH)

        if response.status_code == 200:
            return response.json().get("ticket_metric", {})
        
        return {"error": f"Failed to fetch metrics for ticket {ticket_id}. Status: {response.status_code}"}

async def send_feedback_to_telex(return_url: str):
    """Fetch Zendesk data and send it to Telex's return URL."""
    tickets = await fetch_support_tickets()
    ratings = await fetch_satisfaction_ratings()

    feedback_data = {
        "tickets": tickets,
        "ratings": ratings
    }

    async with httpx.AsyncClient() as client:
        await client.post(return_url, json=feedback_data)
