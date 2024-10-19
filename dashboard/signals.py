from .models import Event
from django.db.models.signals import post_save
from django.dispatch import receiver
from .microsoft_graph_api import create_teams_meeting  # Assuming your helper functions are in utils.py


@receiver(post_save, sender=Event)
def create_teams_meeting_for_event(sender, instance, created, **kwargs):
    if created:
        event_title = instance.title
        event_date = instance.start_time.isoformat()
        candidate = instance.candidate
        attendees = candidate.email
        meeting_url = create_teams_meeting(event_title, event_date, attendees)

        if meeting_url:
            # You can save the meeting URL to the event or send an email
            print(f"Meeting created: {meeting_url}")