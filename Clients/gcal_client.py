from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import service_account_info

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_info(
        service_account_info(),
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)

def delete_synced_events(service, calendar_id, time_min, time_max, marker):
    existing = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    for event in existing.get("items", []):
        desc = event.get("description", "") or ""
        if marker in desc:
            service.events().delete(calendarId=calendar_id, eventId=event["id"]).execute()

def insert_event(service, calendar_id, body):
    service.events().insert(calendarId=calendar_id, body=body).execute()
