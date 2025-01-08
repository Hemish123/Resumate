from django.db.models.signals import post_save
from django.dispatch import receiver
from candidate.models import Candidate
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from manager.models import JobOpening
from notification.models import Notification


# @receiver(post_save, sender=Notification)
# def send_notification(sender, instance, created, **kwargs):
#     if created:
#         type = "send_message"
#         message = instance.message
#         user_id = instance.user.id
#
#         channel_layer = get_channel_layer()
#         group_name = f'user_{user_id}'
#         event = {
#             'type': type,
#             'message': message,
#             'time': instance.created_at.isoformat()
#         }
#         async_to_sync(channel_layer.group_send)(group_name, event)


