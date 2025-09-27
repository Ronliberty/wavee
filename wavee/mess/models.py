from django.db import models
from django.conf import settings
import uuid


class Message(models.Model):
    """
    Stores chat messages (text, media, etc.)
    """
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"

    MESSAGE_TYPES = [
        (TEXT, "Text"),
        (IMAGE, "Image"),
        (FILE, "File"),
        (VOICE, "Voice"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey("chat.Chat", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")

    content = models.TextField(blank=True, null=True)  # For text messages
    type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default=TEXT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    # Read receipts
    delivered_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="delivered_messages",
        blank=True
    )
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="read_messages",
        blank=True
    )

    def __str__(self):
        return f"{self.type} from {self.sender.phone_number} in {self.chat.id}"


class Attachment(models.Model):
    """
    Stores file/image/voice attachments linked to a message.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")

    file = models.FileField(upload_to="attachments/")  # Stored in S3/MinIO
    file_type = models.CharField(max_length=50)        # mime type
    file_size = models.BigIntegerField()               # in bytes

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.message.id} ({self.file_type})"
