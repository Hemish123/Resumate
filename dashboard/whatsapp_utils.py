# dashboard/whatsapp_utils.py

import requests
from django.conf import settings

WASENDER_URL = "https://wasenderapi.com/api/send-message"


def clean_phone(number: str) -> str:
    """
    Phone number ne international format ma convert kare chhe.
    9879704384     → 919879704384
    +919879704384  → 919879704384
    91 98797 04384 → 919879704384
    """
    if not number:
        return ""
    
    # Remove spaces, dashes, plus
    cleaned = number.replace("+", "").replace(" ", "").replace("-", "").strip()
    
    # If 10 digit Indian number, add 91 prefix
    if len(cleaned) == 10 and cleaned.startswith(("6", "7", "8", "9")):
        cleaned = "91" + cleaned
    
    return cleaned


def send_whatsapp(phone: str, message: str) -> bool:
    """
    Wasender API thi WhatsApp message mokle chhe.
    Returns True if success, False if failed.
    """
    phone = clean_phone(phone)
    if not phone:
        print("WhatsApp: Phone number missing, skipping.")
        return False

    try:
        response = requests.post(
            WASENDER_URL,
            headers={
                "Authorization": f"Bearer {settings.WASENDER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "to": phone,
                "text": message,
            },
            timeout=10,
        )
        response.raise_for_status()
        print(f"WhatsApp sent to {phone}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"WhatsApp HTTP error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.ConnectionError:
        print("WhatsApp: Connection failed.")
    except requests.exceptions.Timeout:
        print("WhatsApp: Request timed out.")
    except Exception as e:
        print(f"WhatsApp unexpected error: {e}")

    return False