from django.urls import path
from .views import NotificationListView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
]

websocket_urlpatterns = [
    path("ws/notification/", NotificationConsumer.as_asgi())
]