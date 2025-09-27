from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.ListUserChatsView.as_view(), name="chat-list"),
    path("private/create/", views.CreatePrivateChatView.as_view(), name="chat-private-create"),
    path("group/create/", views.CreateGroupChatView.as_view(), name="chat-group-create"),
]