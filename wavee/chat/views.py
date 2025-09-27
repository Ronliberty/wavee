from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Chat, ChatMember
from .serializers import ChatSerializer
from users.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny


class ListUserChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chats = Chat.objects.filter(members__user=request.user)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)
    

class CreatePrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):








        
        print("🔹 CreatePrivateChatView hit")
        print("🔹 Headers:", request.headers)
        print("🔹 User:", request.user)
        print("🔹 Data:", request.data)
        
        other_user_id = request.data.get("user_id")
        other_user = get_object_or_404(User, id=other_user_id)

        chat = Chat.objects.filter(
            type=Chat.PRIVATE,
            members_user=request.user

        ).filter(
            members_user=other_user
        ).first()

        if not chat:
            chat = Chat.objects.create(type=Chat.PRIVATE)
            ChatMember.objects.create(chat=chat, user=request.user, role=ChatMember.MEMBER)
            ChatMember.objects.create(chat=chat, user=other_user, role=ChatMember.MEMBER)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=201)
    

class CreateGroupChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        member_ids = request.data.get("member_ids", [])

        if not title:
            return Response({"error": "Name is required"}, status=400)
        
        chat = Chat.objects.create(type=Chat.Group, title=title)
        ChatMember.objects.create(chat=chat, user=request.user, role=ChatMember.OWNER)

        for user_id in member_ids:
            user = get_object_or_404(User, id=user_id)
            ChatMember.objects.create(chat=chat, user=user, role=ChatMember.MEMBER)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=201)