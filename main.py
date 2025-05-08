# main.py
from fastapi import FastAPI, HTTPException,Query
from typing import List
from models import Event, Attendee, Ticket,EventWithTickets
from pydantic import BaseModel
from crud import create_event, get_attendees_for_event, get_events_next_30_days, count_tickets_by_ticket_type, assign_attendee_to_event, create_ticket,book_tickets

app = FastAPI()


class EventQuery(BaseModel):
    event_name: str

# Create Event
@app.post("/events/", response_model=EventWithTickets)
async def create_new_event(payload: EventWithTickets):
    try : 
        event_id,ticket_data = create_event(payload)
        
        return {
            "event": {**payload.event.dict(), "id": event_id},
            "tickets": ticket_data
        }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get Attendees for an Event
@app.get("/events/attendees", response_model=List[Attendee])
async def get_attendees(name: str, location: str):
    attendees = get_attendees_for_event(name,location)
    if attendees == None:
        raise HTTPException(status_code=404, detail="No event found")
    if not attendees:
        raise HTTPException(status_code=404, detail="No Attendees for this event")
    return attendees

# List All Events in the Next 30 Days in a Specific Location
@app.get("/events/upcoming/{location}", response_model=List[Event])
async def get_upcoming_events(location: str):
    events = get_events_next_30_days(location)
    print(len(events))
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    return events


@app.get("/count_tickets")
async def count_tickets(event_name: str):
    try:
        ticket_counts = count_tickets_by_ticket_type(event_name)
        return ticket_counts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/book")
def book_ticket_api(
    ticket_type: str = Query(..., description="Ticket type to be booked"),
    event: Event = ...,  # Event details from request body
    attendee: Attendee = ...,  # Attendee details from request body
):
    try:
        ticket_id = book_tickets(event, ticket_type, attendee)
        return {"message": "Ticket booked successfully", "ticket_id": ticket_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))