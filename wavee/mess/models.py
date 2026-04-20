import uuid
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, blank=True, null=True)
    is_group = models.BooleanField(default=False)


    last_message = models.ForeignKey("Message", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Conversation {self.id}"


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation_participations")


    last_read_at = models.DateTimeField(null=True, blank=True)


    is_archived = models.BooleanField(default=False)


    is_muted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("conversation", "user")


class Message(models.Model):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"

    MESSAGE_TYPES = [
        (TEXT, "Text"),
        (IMAGE, "Image"),
        (FILE, "File"),
        (SYSTEM, "System"),
    ]

    STATUS_CHOICES = [
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("read", "Read"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")

    content = models.TextField(blank=True, null=True)

    type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default=TEXT)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="sent")

    created_at = models.DateTimeField(auto_now_add=True)


    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="read_messages")

    def __str__(self):
        return f"{self.type} - {self.sender_id}"


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")

    file = models.FileField(upload_to="attachments/")

    file_type = models.CharField(max_length=50)
    file_size = models.BigIntegerField()


    file_name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)

    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    thumbnail = models.ImageField(upload_to="attachments/thumbnails/", null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name or self.file} ({self.file_type})"