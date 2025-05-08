from google.cloud import firestore
import os
import random
from datetime import datetime, timedelta
import bcrypt
import uuid
from google.oauth2 import service_account

key_path = "/home/mind/ccompact-surfer-458605-v5-13d21b7c68b2.json"
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials, project=credentials.project_id,database="event-management")

# Initialize Firestore client
# db = firestore.Client()
print(db)
# Sample event data and ticket types
event_names = [
     "Live Concert: The Yellow Diary",
     "AI & ML Tech Conference",
    "Startup Expo 2025", "AI Summit: Keynotes", "Design Fest 2025",
    "Stand-up: Zakir Khan",
    "TEDx: Space Exploration", "Art Exhibition", "Digital Marketing Talk", "Startup Networking",
    "Health & Wellness Expo", "Fitness Challenge '25", "Startup Pitch Fest",
    "Women in Tech","E-commerce Trends '25",
    "Crypto & Blockchain Conf", "Influencer Meet-up", "EdTech Innovation Summit"
]

locations = [
    "Mumbai",
    "Pune", "Ahmedabad"]
ticket_types = [
    {"ticket_type": "Early Bird", "price": 500, "count_range": (2, 3)},
    {"ticket_type": "VIP", "price": 1500, "count_range": (1, 2)},
    {"ticket_type": "Regular", "price": 1000, "count_range": (5, 6)},
]

# Helper function to generate random dates
def random_date(offset=30):
    return datetime.utcnow() + timedelta(days=random.randint(1, offset))

# Function to login via Firestore (check email and password)
def login_user(email, password):
    try:
        # Check if the email exists in Firestore
        user_ref = db.collection("users").document(email)
        user = user_ref.get()
        
        if user.exists:
            user_data = user.to_dict()
            stored_password_hash = user_data['password']  # Assumes 'password' field contains a bcrypt hashed password
            
            # Validate the password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                print(f"User {email} logged in successfully!")
                return True
            else:
                print("Incorrect password.")
                return False
        else:
            print(f"User with email {email} does not exist.")
            return False
    except Exception as e:
        print(f"Error logging in user: {e}")
        return False

# Create event function
def create_event(event_index):
    event_id = f"event_{event_index}"
    event_ref = db.collection("events").document(event_id)
    date = random_date().isoformat()
    event_data = {
        "name": f"{random.choice(event_names)} {2025 + event_index}",
        "location": random.choice(locations),
        "date": random_date().isoformat(),
        "is_active": True,
        "organizer_id": f"user_{random.randint(1, 10)}"
    }
    event_ref.set(event_data)

    # Add ticket types as subcollection with random counts
    for t in ticket_types:
        count = 10*(random.randint(t["count_range"][0], t["count_range"][1]))
        event_ref.collection("ticket_types").add({
            "ticket_type": t["ticket_type"],
            "count": count,
            "price": t["price"]
        })

    return event_id

# Create attendee function
def create_attendee(attendee_index):
    attendee_id = f"attendee_{attendee_index}"
    attendee_data = {
        "name": f"Attendee {attendee_index}",
        "email": f"user{attendee_index}@example.com",
        "phone": f"+91-98765{str(attendee_index).zfill(5)}",
        "is_active": True
    }
    db.collection("attendees").document(attendee_id).set(attendee_data)
    return attendee_id

# Assign attendee to event
def assign_attendee_to_event(event_id, attendee_id):
    event_ref = db.collection("events").document(event_id)
    attendee_ref = db.collection("attendees").document(attendee_id)
    event_ref.collection("attendees").document(attendee_id).set({
        "attendee_ref": attendee_ref,
        "registered_at": datetime.utcnow().isoformat()
    })

# Create ticket for the attendee
def create_ticket(event_id, attendee_id):
    ticket_id = str(uuid.uuid4())
    t_type = random.choice(ticket_types)

    ticket_data = {
        "ticket_type": t_type["ticket_type"],
        "price": t_type["price"],
        "purchase_date": datetime.utcnow().isoformat(),
        "is_active": True,
        "attendee_ref": db.collection("attendees").document(attendee_id),
        "event_ref": db.collection("events").document(event_id)
    }
    db.collection("tickets").document(ticket_id).set(ticket_data)

# Seed Firestore with events and attendees
def seed_firestore_data(event_count=5, attendee_count=100):
    print("Starting data seeding...")
    event_ids = [create_event(i) for i in range(1, event_count + 1)]
    print("Firestore seeded with events.")
    
    # Create and assign attendees
    for i in range(1, attendee_count + 1):
        attendee_id = create_attendee(i)
        event_id = random.choice(event_ids)
        assign_attendee_to_event(event_id, attendee_id)
        create_ticket(event_id, attendee_id)

    print("✅ Attendees and tickets assigned successfully.")

# Main function to execute login and seeding
def main():
    # # Example login:
    # email = "testuser@example.com"
    # password = "password123"  # Password that was hashed and stored in Firestore
    # logged_in = login_user(email, password)
    
    # if logged_in:
        # If login is successful, seed the Firestore data
    seed_firestore_data(event_count=10, attendee_count=100)

if __name__ == "__main__":
    main()
