from .models import Notification

def base_template_context(request):
    if request.user.is_authenticated:
        return {
            'notifications': Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
        }
    return {}