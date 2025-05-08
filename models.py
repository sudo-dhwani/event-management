# models.py
from pydantic import BaseModel
from typing import List, Optional

class TicketType(BaseModel):
    ticket_type: str
    price: float
    count: int

# Event Model
class Event(BaseModel):
    name: str
    location: str
    date: str
    is_active: bool
    organizer_id: str

# Attendee Model
class Attendee(BaseModel):
    name: str
    email: str
    phone: str
    is_active: bool

# Ticket Model
class Ticket(BaseModel):
    ticket_type: str
    price: float
    purchase_date: str
    is_active: bool
    event_id: str
    attendee_id: str
    
class EventWithTickets(BaseModel):
    event: Event
    tickets: List[TicketType]