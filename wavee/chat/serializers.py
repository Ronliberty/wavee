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
    def get_display_name(self, obj):
        request = self.context.get("request")
        current_user = getattr(request, "user", None)
        if not current_user:
            return obj.title or "Unknown"

        if obj.type == Chat.GROUP:
            return obj.title or "Group Chat"

        if obj.type == Chat.PRIVATE:
            # get the other member
            other_member = obj.members.exclude(user=current_user).first()
            if not other_member:
                return "Private Chat"

            other_user = other_member.user

            # check if other_user is in current_user's contacts
            contact_obj = current_user.contacts.filter(contact_user=other_user).first()
            if contact_obj:
                return contact_obj.contact_user.name  # saved contact name

            # fallback to phone/email
            return other_user.phone_number or other_user.email

        return obj.title or "Unknown"



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
    unread_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Chat
        fields = [
            "id",
            "type",
            "title",
            "created_at",
            "members",
            "unread_count",
        ]