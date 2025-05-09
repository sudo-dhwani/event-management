# crud.py
from google.cloud import firestore
from typing import List
from models import Event, Attendee, Ticket,EventWithTickets
from datetime import datetime, timedelta
from config import get_firestore_client
import pandas as pd
from utils import random_date
import random
import uuid 

db = get_firestore_client()

# Create event function
def create_event(payload: EventWithTickets):
    event_data = payload.event
    ticket_data = payload.tickets


    event_data= event_data.dict()
    event_query = db.collection("events") \
        .where("location", "==", event_data["location"]) \
        .where("date", "==", event_data["date"]) \
        .limit(1) 

    existing_events = event_query.get()
    if existing_events:
        raise Exception("Another Event already exists at this time & place")

    event_data["is_active"]= True
    
    event_ref = db.collection("events").document()
    event_ref.set(event_data)
    event_id = event_ref.id
    # Add ticket types as subcollection with random counts
    for t in ticket_data:
        event_ref.collection("ticket_types").add({
            "ticket_type": t.ticket_type,
            "count": t.count,
            "price": t.price
        })

    return event_id, ticket_data


def create_or_get_attendee(attendee: Attendee) -> str:
    attendees_ref = db.collection("attendees")
    query = attendees_ref.where("email", "==", attendee.email).limit(1)
    docs = list(query.stream())

    if docs:
        return docs[0]  

    doc_ref = attendees_ref.document()
    doc_ref.set(attendee.dict())
    return doc_ref

def assign_attendee_to_event(event_id: str, attendee_id: str):
    event_ref = db.collection("events").document(event_id)
    attendee_ref = db.collection("attendees").document(attendee_id)
    event_ref.collection("attendees").document(attendee_id).set({
        "attendee_ref": attendee_ref,
        "registered_at": datetime.utcnow().isoformat()
    })

def create_ticket(event_id, attendee_id,ticket_type, price,expires_at):
    tickets_ref = db.collection("tickets").where("attendee_ref", "==", db.collection("attendees").document(attendee_id)) \
                                            .where("event_ref", "==", db.collection("events").document(event_id))
    existing_tickets = tickets_ref.get()

    if existing_tickets:
        raise Exception(f"Attendee {attendee_id} has already booked a ticket for this event.")

    ticket_id = str(uuid.uuid4())
    ticket_data = {
        "ticket_type": ticket_type,
        "price": price,
        "purchase_date": datetime.utcnow().isoformat(),
        "is_active": True,
        "attendee_ref": db.collection("attendees").document(attendee_id),
        "event_ref": db.collection("events").document(event_id),
        "expires_at":expires_at
    }
    db.collection("tickets").document(ticket_id).set(ticket_data)
    return ticket_id

def get_attendees_for_event(name,location) -> List[Attendee]:
    event_query = db.collection("events").where("name", "==", name).where("location", "==", location).get()
    if not event_query:
        return None
    event_doc = event_query[0]
    event_ref = db.collection("events").document(event_doc.id)
    attendees_ref = event_ref.collection("attendees")
    attendees = attendees_ref.stream()

    result = []
    for attendee in attendees:
        print(attendee)
        data = attendee.to_dict()
        attendee_ref = data.get("attendee_ref")
        if attendee_ref:
            attendee_doc = attendee_ref.get()
            attendee_data = attendee_doc.to_dict()
            if attendee_data:
                result.append(Attendee(**attendee_data))

    return result

def get_events_next_30_days(location: str) -> List[Event]:
    now = datetime.utcnow()
    end_date = now + timedelta(days=30)

    events_ref = db.collection("events")
    events_query = events_ref.where("location", "==", location) \
                              .where("date", ">=", now.isoformat()) \
                              .where("date", "<=", end_date.isoformat())
    events = events_query.stream()
    return [Event(**event.to_dict()) for event in events]


def count_tickets_by_ticket_type(event_name: str):
    try:
        event_ref = db.collection("events").where("name", "==", event_name).limit(1).get()
        
        if not event_ref:
            raise Exception("Event not found")

        event_doc = event_ref[0]
        event_ref = event_doc.reference

        tickets_ref = db.collection("tickets").where("event_ref", "==", event_ref)
        
        tickets_df = pd.DataFrame([ticket.to_dict() for ticket in tickets_ref.stream()])

        if tickets_df.empty:
            return {"message": "No tickets found for this event."}

        ticket_counts = tickets_df['ticket_type'].value_counts().to_dict()

        return ticket_counts
    
    except Exception as e:
        raise Exception(f"Error occurred: {str(e)}")

def book_tickets(event: Event, ticket_type: str, attendee: Attendee):
    event_ref_id = db.collection("events").where("name", "==", event.name).where("location" , "==",event.location).where("date","==",event.date)
    event_doc = event_ref_id.get()
    if not event_doc:
        raise Exception("Event not found")

    event_ref = event_doc[0]
    event_ref = db.collection("events").document(event_ref.id)
    ticket_type_ref = event_ref.collection("ticket_types").where("ticket_type" , "==", ticket_type)
    ticket_type_doc = ticket_type_ref.get()
    if not ticket_type_doc:
        raise Exception("Ticket type not found")

    ticket_data = ticket_type_doc[0].to_dict()

    
    tickets_ref = db.collection("tickets").where("event_ref", "==", event_ref).where("ticket_type", "==", ticket_type)
    tickets = tickets_ref.get()
    booked_count = len(tickets)

    # booked_count = ticket_data.get("booked_count", 0)
    capacity = ticket_data.get("count", 0)
    event_date = event_doc[0].to_dict().get("date")
    if event_date:
        event_date_obj = datetime.strptime(event.date, "%Y-%m-%dT%H:%M:%S.%f")
        expires_at = event_date_obj + timedelta(milliseconds=10)
        expires_at_str = expires_at.isoformat()
    else:
        raise Exception("Event date not found")
    if booked_count >= capacity:
        raise Exception("Ticket capacity reached")
    else:
        attendee_ref = create_or_get_attendee(attendee)
        print(attendee_ref)
        price= ticket_data.get("price",0)
        assign_attendee_to_event(event_ref.id, attendee_ref.id)
        ticket_id = create_ticket(event_ref.id, attendee_ref.id,ticket_type, price,expires_at_str)


    return {
        "message": "Ticket booked successfully",
        "event_id": event_ref.id,
        "event_name" :event_doc[0].get("name"),
        "ticket_type": ticket_type,
        "attendee": attendee_ref.get("name"),
        "attendee_id": attendee_ref.id,
        "attendee_email": attendee_ref.get("email"),
        "phone":attendee_ref.get("phone"),
        "ticket_id"  : ticket_id

    }