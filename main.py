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



def get_setting_by_label(settings, label):
    for setting in settings:
        if setting.get("label") == label:
            return setting.get("default")
    return None
# Store the latest Zendesk data


@app.get("/integration.json")
async def get_integration_json(request: Request):
    """Returns integration details for Telex."""
    base_url = str("https://tfklhl45-8000.uks1.devtunnels.ms")
    return {
        "data": {
            "descriptions": {
                "app_name": "Zendesk Feedback Monitor",
                "app_description": "Fetches and displays user feedback from Zendesk",
                "app_url": base_url,
                "app_logo": "https://i.imgur.com/lzyyfp.png",
                "background_color": "#fff",
            },
            "integration_category": "CRM & Customer Support",
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
            "target_url": f"{base_url}/tick",
        }
    }



@app.post("/tick", status_code=202)
async def telex_tick(payload: dict, background_tasks: BackgroundTasks):
    """Receives Telex tick request and processes it with provided Zendesk credentials."""

    return_url = payload.get("return_url")
    zendesk_subdomain = get_setting_by_label(payload.get("settings"), label="zendesk_subdomain")
    zendesk_email = get_setting_by_label(payload.get("settings"), label="zendesk_email")
    zendesk_api_token = get_setting_by_label(payload.get("settings"), label="zendesk_api_token")
    
    if not all([return_url, zendesk_subdomain, zendesk_email, zendesk_api_token]):
        return JSONResponse(content={"error": "Missing Zendesk credentials"}, status_code=400)

    background_tasks.add_task(send_feedback_to_telex, return_url, zendesk_subdomain, zendesk_email, zendesk_api_token)
    
    
    return JSONResponse(content={"status": "accepted"})


