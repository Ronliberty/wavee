from django.urls import path
from .views import (
    ConversationListView,
    ConversationDetailView,
    MessageListView,
    SendMessageView,
    MarkAsReadView,
    StartConversationView,
)

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversation-list"),
    path("conversations/<uuid:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),

    path("conversations/<uuid:conversation_id>/messages/", MessageListView.as_view(), name="message-list"),
    path("conversations/start/", StartConversationView.as_view(), name="start-conversation"),

    path("messages/send/", SendMessageView.as_view(), name="send-message"),
    path("messages/<uuid:message_id>/read/", MarkAsReadView.as_view(), name="mark-read"),
]