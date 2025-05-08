# config.py
import os
from google.cloud import firestore
from google.oauth2 import service_account

# Initialize Firestore client
def get_firestore_client():

    key_path = "/home/mind/compact-surfer-458605-v5-13d21b7c68b2.json"
    credentials = service_account.Credentials.from_service_account_file(key_path)
    db = firestore.Client(credentials=credentials, project=credentials.project_id,database="event-management")
    return db