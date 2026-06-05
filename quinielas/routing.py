from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/quiniela/(?P<slug>[\w-]+)/$', consumers.QuinielaConsumer.as_asgi()),
]
