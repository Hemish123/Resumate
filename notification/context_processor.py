from .models import Notification

def base_template_context(request):
    return {
        'notifications': Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
    }