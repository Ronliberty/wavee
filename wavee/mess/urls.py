from django.urls import path
from . import views


urlpatterns = [
    path("list/<uuid:chat_id>/", views.ListMessagesView.as_view(), name="message-list"),
    path("send/", views.SendMessageView.as_view(), name="messages-send"),
    path("read/<uuid:message_id>/", views.MarkMessageReadView.as_view(), name="messages-read"),
]
