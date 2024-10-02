"""
ASGI config for recruit_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruit_management.settings')

application = get_asgi_application()
from notification import urls

application = ProtocolTypeRouter({
    "http": application,
    "websocket": URLRouter(urls.websocket_urlpatterns)
})