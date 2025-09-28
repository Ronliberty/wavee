from rest_framework import serializers
from .models import Chat, ChatMember

from users.serializers import CurrentUserSerializer
from users.models import User
from mess.models import Message
class ChatMemberSerializer(serializers.ModelSerializer):
    user = CurrentUserSerializer(read_only=True)

    class Meta:
        model = ChatMember
        fields = ['id', 'user', "role", 'joined_at']


# class ChatSerializer(serializers.ModelSerializer):
#     members = ChatMemberSerializer(many=True, read_only=True)

#     class Meta:
#         model = Chat
#         fields = ['id', 'type', 'title', 'avatar', 'create_at', 'members']



class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "email", "username"]  # add fields you want
        read_only_fields = fields


class ChatMemberSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = ChatMember
        fields = ["id", "user", "role"]
     

class ChatSerializer(serializers.ModelSerializer):
    members = ChatMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "type", "title", "avatar", "created_at", "members"]


# class ChatListSerializer(serializers.ModelSerializer):
#     """Used for listing chats with extra display info"""
#     display_name = serializers.SerializerMethodField()
#     avatar_url = serializers.SerializerMethodField()
#     last_message = serializers.SerializerMethodField()

#     class Meta:
#         model = Chat
#         fields = [
#             "id",
#             "type",
#             "title",
#             "display_name",
#             "avatar_url",
#             "last_message",
#             "created_at",
#             "members",
#         ]

#     def get_display_name(self, obj):
#         request = self.context.get("request")
#         user = getattr(request, "user", None)

#         # For group chats, use the title
#         if obj.type == "group":
#             return obj.title

#         # For 1-to-1 chats, show the other member's phone number
#         if obj.type == "direct" and user:
#             other = obj.members.exclude(id=user.id).first()
#             return getattr(other.profile, "phone_number", other.username)

#         return obj.title or "Unknown"

#     def get_avatar_url(self, obj):
#         request = self.context.get("request")
#         if obj.type == "group" and obj.avatar:
#             return request.build_absolute_uri(obj.avatar.url)
#         if obj.type == "direct" and request and request.user:
#             other = obj.members.exclude(id=request.user.id).first()
#             if other and other.profile.avatar:
#                 return request.build_absolute_uri(other.profile.avatar.url)
#         return None

#     def get_last_message(self, obj):
#         last_msg = obj.messages.order_by("-created_at").first()
#         return last_msg.content if last_msg else None




class ChatListSerializer(serializers.ModelSerializer):
    """Serializer for listing chats with display info"""
    display_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            "id",
            "type",
            "title",
            "display_name",
            "avatar_url",
            "last_message",
            "created_at",
            "members",
        ]

    def get_display_name(self, obj):
        request = self.context.get("request")
        current_user = getattr(request, "user", None)

        if obj.type == "group":
            return obj.title or "Group Chat"

    # direct/private chat
        if obj.type == "private" and current_user:
            other_member = obj.members.exclude(user_id=current_user.id).first()
            if other_member:
                other_user = other_member.user  # directly get the User
                return getattr(other_user, "phone_number", other_user.email)
    
        return obj.title or "Unknown"


    def get_avatar_url(self, obj):
        # Group chat avatar
        if obj.type == Chat.GROUP:
            return obj.avatar.url if obj.avatar else None

        # Private chat: show other user's avatar
        request = self.context.get("request")
        current_user = getattr(request, "user", None)
        if obj.type == Chat.PRIVATE and current_user:
            other_member = obj.members.exclude(user_id=current_user.id).first()
            if other_member:
                other_user = other_member.user
                # Return avatar URL if exists
                return other_user.avatar.url if getattr(other_user, "avatar", None) else None

        return None

    def get_last_message(self, obj):
        # Return the content of the last message
        last = obj.messages.order_by("-created_at").first()
        if last:
            return last.content
        return None
