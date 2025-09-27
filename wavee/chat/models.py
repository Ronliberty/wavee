from django.db import models
from django.conf import settings
import uuid

class Chat(models.Model):
    PRIVATE = "private"
    GROUP = "group"
    CHAT_TYPES = [
        (PRIVATE, "private"),
        (GROUP, "group"),

    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=CHAT_TYPES, default=PRIVATE)
    title = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to='chat_avatars/', blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.type == self.PRIVATE:
            return f"Private Chat {self.id}"
        return f"Group Chat: {self.title or self.id}"
    

class ChatMember(models.Model):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


    ROLE_CHOICES = [
        (OWNER, "owner"),
        (ADMIN, "admin"),
        (MEMBER, "member"),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("chat", "user")

    def __str__(self):
        return f"{self.user.phone_number} in {self.chat.id} ({self.role})"

