from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import asyncio
from services.zendesk import *


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
fetch_interval = 5  # Default interval in minutes

async def fetch_and_store_data():
    """Fetches data from Zendesk and updates latest_zendesk_data."""
    global latest_zendesk_data
    try:
        feedback = await fetch_support_tickets()
        ratings = await fetch_satisfaction_ratings()

        ticket_metrics = {
            ticket["id"]: await fetch_ticket_metrics(ticket["id"]) for ticket in feedback
        }

        latest_zendesk_data = {
            "feedback": feedback,
            "satisfaction_ratings": ratings,
            "ticket_metrics": ticket_metrics,
            "last_updated": datetime.utcnow(),
        }
        print("✅ Zendesk data updated:", latest_zendesk_data)

    except Exception as e:
        print(f"❌ Error fetching Zendesk data: {e}")

def run_fetch_and_store_data():
    """Runs the async function inside a proper event loop."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(fetch_and_store_data())  # ✅ Correct way to run async task
    else:
        asyncio.run(fetch_and_store_data())

# Set up APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_fetch_and_store_data, "interval", minutes=fetch_interval)
scheduler.start()

# Ensure APScheduler stops gracefully when FastAPI shuts down
atexit.register(lambda: scheduler.shutdown())

# Routes
@app.get("/zendesk-feedback")
def get_feedback():
    """Retrieve the latest Zendesk support tickets."""
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
            "integration_type": "interval",
            "settings": [
                {"label": "zendesk_subdomain", "type": "text", "required": True, "default": ""},
                {"label": "zendesk_email", "type": "text", "required": True, "default": ""},
                {"label": "zendesk_api_token", "type": "text", "required": True, "default": ""},
                {"label": "interval", "type": "text", "required": True, "default": "*/5 * * * *"},  # Every 5 minutes
            ],
            "tick_url": f"{base_url}/tick",
        }
    }


@app.post("/tick", status_code=202)
async def telex_tick(payload: dict, background_tasks: BackgroundTasks):
    """Receives Telex tick request and processes it in the background."""
    return_url = payload.get("return_url")
    background_tasks.add_task(send_feedback_to_telex, return_url)
    return JSONResponse(content={"status": "accepted"})


@app.post("/update-interval")
def update_interval(minutes: int, background_tasks: BackgroundTasks):
    """Dynamically update the fetch interval."""
    global fetch_interval, scheduler
    fetch_interval = minutes
    scheduler.remove_all_jobs()
    scheduler.add_job(run_fetch_and_store_data, "interval", minutes=fetch_interval)
    background_tasks.add_task(fetch_and_store_data)
    return {"message": f"Fetch interval updated to {fetch_interval} minutes."}
