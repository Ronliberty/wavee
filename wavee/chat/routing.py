from django.urls import re_path
from . import consumers

websockets_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_id>[0-9a-f-]+)/$", consumers.ChatConsumer.as_asgi()),
]