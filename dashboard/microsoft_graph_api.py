import msal


def get_access_token():
    # Replace with your actual values
    client_id = "797a5c7f-5eae-4b4d-85d7-8a8f73a6d38c"
    client_secret = "Xdj8Q~a7XM9QAWMWQo-qHjgv6uVUP3xBNffRibD5"
    tenant_id = "d902dae3-a93d-4dbb-86cd-56fed3603160"
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Could not obtain access token")


import requests



def create_teams_meeting(event_title, event_date, attendees):
    access_token = get_access_token()
    url = "https://graph.microsoft.com/v1.0/me/onlineMeetings"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "startDateTime": event_date,  # Format: '2023-10-19T14:30:00Z'
        "endDateTime": event_date,  # Add proper end time
        "subject": event_title,
        "participants": {
            "attendees": [
                {"identity": {"userPrincipalName": attendees}} for attendee in attendees
            ]
        }
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 201:
        meeting_data = response.json()
        return meeting_data["joinUrl"]  # Returns the Teams meeting URL
    else:
        print("Error creating meeting:", response.json())
        return None
