from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import Notification
from django.utils import timezone
from datetime import timedelta

# Create your views here.
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification/notification_list.html'
    context_object_name = 'notifications_list'

    def get_queryset(self):
        # Filter notifications for the logged-in user and show only unread ones
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        threshold_date = timezone.now() - timedelta(days=30)
        Notification.objects.filter(created_at__lt=threshold_date).delete()
        Notification.objects.filter(user=request.user, read=False).update(read=True)

        return super().get(request, *args, **kwargs)