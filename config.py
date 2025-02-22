import os
from dotenv import load_dotenv

load_dotenv()

ZENDESK_URL = os.getenv("ZENDESK_URL")
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")
