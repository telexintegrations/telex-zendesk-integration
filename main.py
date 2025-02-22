from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
from services.zendesk import *
from config import ZENDESK_URL, ZENDESK_EMAIL, ZENDESK_API_TOKEN

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the latest Zendesk data
latest_zendesk_data = {}

async def fetch_and_store_data(subdomain: str, email: str, api_token: str):
    """Fetches data from Zendesk using provided credentials and updates latest_zendesk_data."""
    global latest_zendesk_data
    try:
        feedback = await fetch_support_tickets(subdomain, email, api_token)
        ratings = await fetch_satisfaction_ratings(subdomain, email, api_token)

        ticket_metrics = {
            ticket["id"]: await fetch_ticket_metrics(subdomain, email, api_token, ticket["id"])
            for ticket in feedback
        }

        latest_zendesk_data = {
            "feedback": feedback,
            "satisfaction_ratings": ratings,
            "ticket_metrics": ticket_metrics,
            "last_updated": datetime.utcnow(),
        }
        print("Zendesk data updated:", latest_zendesk_data)

    except Exception as e:
        print(f"Error fetching Zendesk data: {e}")


# Routes
@app.get("/zendesk-feedback")
async def get_feedback():
    """Retrieve the latest Zendesk support tickets."""
    if not latest_zendesk_data:
        await fetch_and_store_data()
    
    return latest_zendesk_data

@app.get("/integration.json")
async def get_integration_json(request: Request):
    """Returns integration details for Telex."""
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "descriptions": {
                "app_name": "Zendesk Feedback Monitor",
                "app_description": "Fetches and displays user feedback from Zendesk",
                "app_url": base_url,
                "app_logo": "https://i.imgur.com/lzyyfp.png",
                "background_color": "#fff",
            },
            "integration_category": " CRM & Customer Support",
            "integration_type": "interval",
            "is_active": True,
            "key_features": [
                "Automatically fetch Zendesk support tickets",
                "Retrieve and analyze customer satisfaction ratings",
                "Monitor ticket metrics for performance insights",
                "Easily integrate with Telex for real-time updates",
            ],
            "settings": [
                {"label": "zendesk_subdomain", "type": "text", "required": True, "default": ""},
                {"label": "zendesk_email", "type": "text", "required": True, "default": ""},
                {"label": "zendesk_api_token", "type": "text", "required": True, "default": ""},
                {"label": "interval", "type": "text", "required": True, "default": "*/5 * * * *"},
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": "",
        }
    }

@app.post("/tick", status_code=202)
async def telex_tick(payload: dict, background_tasks: BackgroundTasks):
    """Receives Telex tick request and processes it with provided Zendesk credentials."""

    return_url = payload.get("return_url")
    zendesk_subdomain = payload.get("zendesk_subdomain")
    zendesk_email = payload.get("zendesk_email")
    zendesk_api_token = payload.get("zendesk_api_token")

    if not all([zendesk_subdomain, zendesk_email, zendesk_api_token]):
        return JSONResponse(content={"error": "Missing Zendesk credentials"}, status_code=400)

    background_tasks.add_task(fetch_and_store_data, zendesk_subdomain, zendesk_email, zendesk_api_token)
    
    return JSONResponse(content={"status": "accepted"})
