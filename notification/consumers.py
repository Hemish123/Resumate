from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template


class NotificationConsumer(WebsocketConsumer):

    def connect(self):

        self.group_name = f"user_{self.scope["user"].id}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        self.accept()


    # def receive(self, text_data=None, bytes_data=None):


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        # Called when the socket closes

    def new_application(self, event):
        html = get_template("notification/notification.html").render(
            context={"message": event["message"]}
        )
        print('html', html)
        self.send(text_data=html)