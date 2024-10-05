from django.db.models.signals import post_save
from django.dispatch import receiver
from candidate.models import Candidate
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from manager.models import JobOpening
from notification.models import Notification


@receiver(post_save, sender=Candidate)
def send_notification_on_new_application(sender, instance, created, **kwargs):
    if created:
        job_opening_id = getattr(instance, 'job_opening_id_temp', None)
        job_opening = JobOpening.objects.get(id=job_opening_id)
        type = "new_application"
        message = instance.name + " applied for " + job_opening.designation
        employees = job_opening.assignemployee.all()
        for e in employees:
            notification = Notification.objects.create(user_id=e.user.id, message=message)
            send_notification(e.user.id, type, message, notification)

        manager = job_opening.created_by
        if manager:
            notification = Notification.objects.create(user_id=manager.id, message=message)
            send_notification(manager.id, type, message, notification)


def send_notification(user_id, type, message, notification):
    channel_layer = get_channel_layer()
    group_name=f'user_{user_id}'
    event = {
            'type': type,
            'message': message,
            'time': notification.created_at.isoformat()
        }
    async_to_sync(channel_layer.group_send)(group_name, event)