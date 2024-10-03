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
        print('id', job_opening_id)
        job_opening = JobOpening.objects.get(id=job_opening_id)
        type = "new_application"
        message = "New application received for " + job_opening.designation
        employees = job_opening.assignemployee.all()
        for e in employees:
            Notification.objects.create(user__id=e.user.id, message=message)
            send_notification(e.user.id, type, message)

        manager = job_opening.created_by
        if manager:
            Notification.objects.create(user__id=manager.id, message=message)
            send_notification(manager.id, type, message)
        print(f'Notification: A new application was created with ID {instance.id}')


def send_notification(user_id, type, message):
    channel_layer = get_channel_layer()
    group_name=f'user_{user_id}'
    event = {
            'type': type,
            'message': message
        }
    print('mes')
    async_to_sync(channel_layer.group_send)(group_name, event)