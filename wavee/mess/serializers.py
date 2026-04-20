from rest_framework import serializers
from .models import Message, Attachment, Conversation, ConversationParticipant


class MessageSerializer(serializers.ModelSerializer):
    conversationId = serializers.UUIDField(source="conversation.id", read_only=True)
    senderId = serializers.UUIDField(source="sender.id", read_only=True)
    timestamp = serializers.DateTimeField(source="created_at", read_only=True)

    isRead = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "conversationId",
            "senderId",
            "content",
            "timestamp",
            "isRead",
            "status",
            "type",
        ]

    def get_isRead(self, obj):
        user = self.context.get("request").user
        return obj.read_by.filter(id=user.id).exists()




class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "id",
            "file",
            "file_type",
            "file_size",
            "file_name",
            "mime_type",
            "width",
            "height",
            "thumbnail",
        ]





class ConversationSerializer(serializers.ModelSerializer):
    lastMessage = serializers.SerializerMethodField()
    lastMessageTime = serializers.SerializerMethodField()
    unreadCount = serializers.SerializerMethodField()

    isGroup = serializers.BooleanField(source="is_group")
    participants = serializers.SerializerMethodField()
    isArchived = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "lastMessage",
            "lastMessageTime",
            "unreadCount",
            "isGroup",
            "isArchived",
            "participants",
        ]


    def get_lastMessage(self, obj):
        if obj.last_message:
            return obj.last_message.content
        return ""


    def get_lastMessageTime(self, obj):
        if obj.last_message:
            return obj.last_message.created_at
        return None


    def get_unreadCount(self, obj):
        user = self.context.get("request").user

        participant = obj.participants.filter(user=user).first()
        if not participant or not participant.last_read_at:
            return obj.messages.count()

        return obj.messages.filter(
            created_at__gt=participant.last_read_at
        ).count()


    def get_participants(self, obj):
        return list(
            obj.participants.values_list("user__id", flat=True)
        )


    def get_isArchived(self, obj):
        user = self.context.get("request").user

        participant = obj.participants.filter(user=user).first()
        return participant.is_archived if participant else False





class StartConversationSerializer(serializers.Serializer):
    contact_name = serializers.CharField(required=True, max_length=255)

    def validate_contact_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Contact name cannot be empty.")
        return value