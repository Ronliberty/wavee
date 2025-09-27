from rest_framework import serializers
from .models import Chat, ChatMember

from users.serializers import CurrentUserSerializer


class ChatMemberSerializer(serializers.ModelSerializer):
    user = CurrentUserSerializer(read_only=True)

    class Meta:
        model = ChatMember
        fields = ['id', 'user', "role", 'joined_at']


class ChatSerializer(serializers.ModelSerializer):
    members = ChatMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'type', 'title', 'avatar', 'create_at', 'members']


        

        