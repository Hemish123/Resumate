# app_name/templatetags/custom_filters.py
from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def timesince_custom(value):
    now = datetime.now()
    diff = now - value

    if diff.days >= 1:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"
