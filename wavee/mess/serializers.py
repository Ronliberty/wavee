from rest_framework import serializers
from .models import Message, Attachment
from users.serializers import CurrentUserSerializer
from chat.serializers import ChatSerializer



class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ["id", "file", "file_type", "file_size", "uploaded_at"]

    def get_file(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class MessageSerializer(serializers.ModelSerializer):
    sender = CurrentUserSerializer(read_only=True)
    chat = ChatSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    delivered_to = CurrentUserSerializer(many=True, read_only=True)
    read_by = CurrentUserSerializer(many=True, read_only=True)


    class Meta:
        model = Message
        fields = [
            "id",
            "chat",
            "sender",
            "content",
            "type",
            "attachments",
            "created_at",
            "updated_at",
            "is_deleted",
            "delivered_to",
            "read_by",
        ]


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["chat", "content", "type"]
