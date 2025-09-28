from django.contrib import admin
from .models import Chat, ChatMember

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "title", "created_at")
    search_fields = ("title",)
    list_filter = ("type", "created_at")

@admin.register(ChatMember)
class ChatMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "user", "role")
    search_fields = ("user__username", "user__phone_number")