from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime, timedelta

key_path = "/home/mind/ccompact-surfer-458605-v5-13d21b7c68b2.json"
credentials = service_account.Credentials.from_service_account_file(key_path)
db = firestore.Client(credentials=credentials, project=credentials.project_id,database="event-management")

def set_expires_at_on_tickets():
    tickets_ref = db.collection("tickets")
    tickets = tickets_ref.stream()
    updated = 0

    for ticket in tickets:
        data = ticket.to_dict()
        event_ref = data.get("event_ref")
        if not event_ref:
            continue

        try:
            event_doc = event_ref.get()
            event_data = event_doc.to_dict()

            if not event_data or "date" not in event_data:
                continue

            
            end_date = datetime.fromisoformat(event_data["date"])
            expires_at = end_date + timedelta(milliseconds=10)

            
            ticket.reference.update({"expires_at": expires_at})
            updated += 1

        except Exception as e:
            print(f"Error with ticket {ticket.id}: {e}")

    print(f"Updated {updated} tickets with 'expires_at'.")

if __name__ == "__main__":
    set_expires_at_on_tickets()
