# pubsub_client.py

from google.cloud import pubsub_v1
from google.oauth2 import service_account
import os, json

credentials = service_account.Credentials.from_service_account_file(
    "/home/mind/compact-surfer-458605-v5-13d21b7c68b2.json"
)


project_id = credentials.project_id
topic_id = "ticket-booked"

publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(project_id, topic_id) #making queue types


def publish_ticket_event(ticket_data: dict):
    message_bytes = json.dumps(ticket_data).encode("utf-8")
    future = publisher.publish(topic_path, message_bytes)
    print(f"Published message ID: {future.result()}")