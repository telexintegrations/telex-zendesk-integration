from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class Ticket(BaseModel):
    id: int
    subject: str
    status: str
    created_at: datetime

class SatisfactionRating(BaseModel):
    ticket_id: int
    score: Optional[int]
    comment: Optional[str]

class TicketMetric(BaseModel):
    ticket_id: int
    reply_time: Optional[str]
    resolution_time: Optional[str]

class ZendeskFeedbackResponse(BaseModel):
    feedback: List[Ticket]
    satisfaction_ratings: List[SatisfactionRating]
    ticket_metrics: Dict[int, TicketMetric]

class TelexData(BaseModel):
    date: Dict[str, datetime]
    descriptions: Dict[str, str]
    integration_category: str
    integration_type: str
    is_active: bool
    output: List[Dict[str, str]]
    key_features: List[str]
    permissions: Dict[str, Dict[str, str]]
    settings: Dict[str, str]
