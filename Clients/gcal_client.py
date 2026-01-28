"""
Google Calendar client utilities.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import service_account_info

def get_calendar_service():
    """
    Create an authenticated Google Calendar service client.

    Returns:
        googleapiclient.discovery.Resource: Calendar API service instance.
    """
    creds = service_account.Credentials.from_service_account_info(
        service_account_info(),
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)

def delete_synced_events(service, calendar_id, time_min, time_max, marker):
    """
    Delete previously synced events from a Google Calendar.

    Removes all events within the specified time range whose description
    contains the sync marker.

    Args:
        service: Authenticated Google Calendar service.
        calendar_id: Target calendar ID.
        time_min: RFC3339 start time.
        time_max: RFC3339 end time.
        marker: Text marker identifying synced events.
    Returns:
        None
    """
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
    """
    Insert an event into a Google Calendar.

    Args:
        service: Authenticated Google Calendar service.
        calendar_id: Target calendar ID.
        body: Event details.
    Returns:
        None
    """ 
    service.events().insert(calendarId=calendar_id, body=body).execute()
