from django.urls import path
from .views import NotificationListView
from.consumers import NotificationConsumer

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
]

