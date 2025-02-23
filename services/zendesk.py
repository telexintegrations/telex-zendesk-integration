import httpx
import os
from config import ZENDESK_URL, ZENDESK_EMAIL, ZENDESK_API_TOKEN


AUTH = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)
def get_auth(zendesk_email, zendesk_api_token):
    return (f"{zendesk_email}/token", zendesk_api_token)

async def fetch_support_tickets(zendesk_subdomain, zendesk_email, zendesk_api_token):
    """Fetches support tickets from Zendesk."""
    zendesk_api_url = f"{zendesk_subdomain}/api/v2/tickets.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(zendesk_api_url, auth=get_auth(zendesk_email, zendesk_api_token))

        if response.status_code == 200:
            tickets = response.json().get("tickets", [])
            return [{"id": t["id"], "subject": t["subject"], "status": t["status"]} for t in tickets]
        
        return {"error": f"Failed to fetch tickets. Status: {response.status_code}"}

async def fetch_satisfaction_ratings(zendesk_subdomain, zendesk_email, zendesk_api_token):
    """Fetches customer satisfaction ratings from Zendesk."""
    url = f"{zendesk_subdomain}/api/v2/satisfaction_ratings.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, auth=get_auth(zendesk_email, zendesk_api_token))

        if response.status_code == 200:
            data = response.json()
            return [{"id": r["id"], "score": r["score"], "comment": r.get("comment", "No comment")} for r in data.get("satisfaction_ratings", [])]
        
        return {"error": f"Failed to fetch ratings. Status: {response.status_code}"}


async def send_feedback_to_telex(return_url: str, zendesk_subdomain, zendesk_email, zendesk_api_token ):
    """Fetch Zendesk data and send it to Telex's return URL."""
    tickets = await fetch_support_tickets(zendesk_subdomain, zendesk_email, zendesk_api_token)
    ratings = await fetch_satisfaction_ratings(zendesk_subdomain, zendesk_email, zendesk_api_token)
    # metrics = await fetch_ticket_metrics(zendesk_subdomain, zendesk_email, zendesk_api_token)?

    feedback_data = {
        "tickets": tickets,
        "ratings": ratings,
        # "metrics": metrics,
    }

    payload = {
    "event_name": "Zendesk feedback",
    "message": f"{feedback_data}",
    "status": "success",
    "username": "BlessOnyi"
    }


    async with httpx.AsyncClient() as client:
        await client.post(return_url, json=payload)
        print("Paylaod successfully sent to telex")
