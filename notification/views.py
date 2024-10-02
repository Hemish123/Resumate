from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import Notification


# Create your views here.
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        # Filter notifications for the logged-in user and show only unread ones
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')