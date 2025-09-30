from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Chat, ChatMember
from .serializers import ChatSerializer, ChatListSerializer
from users.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import F, Count, OuterRef, Subquery
from django.db import transaction

# class ListUserChatsView(APIView):
#     permission_classes = [IsAuthenticated]


#     def get(self, request):
#         chats = Chat.objects.filter(members__user=request.user)
#         serializer = ChatListSerializer(chats, many=True)
#         return Response(serializer.data)



# class ListUserChatsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         tab = request.query_params.get("tab", "all")
#         chats = Chat.objects.filter(members__user=request.user).distinct()
#         if tab == "group":
#             chats = chats.filter(type=Chat.GROUP)
#         elif tab == "private":
#             chats = chats.filter(type=Chat.PRIVATE)
#         elif tab == "unread":
#             chats = chats.filter(
#                 members__user=request.user,
#                 messages__created_at__gt=F("members__last_read_at")
#             ).distinct()
#         chat_data = []

#         for chat in chats:
#             # 1️⃣ Determine display_name
#             if chat.type == Chat.GROUP:
#                 display_name = chat.title or "Group Chat"
#             elif chat.type == Chat.PRIVATE:
#                 other_member = chat.members.exclude(user=request.user).first()
#                 if not other_member:
#                     display_name = "Private Chat"
#                 else:
#                     other_user = other_member.user
#                     contact_obj = request.user.contacts.filter(contact_user=other_user).first()
#                     if contact_obj:
#                         display_name = contact_obj.contact_user.name
#                     else:
#                         display_name = str(other_user.phone_number) if other_user.phone_number else other_user.email
#             else:
#                 display_name = chat.title or "Unknown"

#             # 2️⃣ Determine avatar URL
#             if chat.type == Chat.GROUP:
#                 avatar_url = chat.avatar.url if chat.avatar else None
#             elif chat.type == Chat.PRIVATE and other_member:
#                 avatar_url = other_user.avatar.url if getattr(other_user, "avatar", None) else None
#             else:
#                 avatar_url = None

#             # 3️⃣ Determine last message
#             last_message_obj = chat.messages.order_by("-created_at").first()
#             last_message = last_message_obj.content if last_message_obj else None

#             # Serialize base chat fields
#             serializer = ChatListSerializer(chat)
#             data = serializer.data

#             # Inject custom fields
#             data.update({
#                 "display_name": display_name,
#                 "avatar_url": avatar_url,
#                 "last_message": last_message,
#             })

#             chat_data.append(data)

#         return Response(chat_data)



class ListUserChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tab = request.query_params.get("tab", "all")  # all, group, private, unread

        # Base queryset: chats the user is a member of
        chats = Chat.objects.filter(members__user=request.user).distinct()

        # Filter by tab
        if tab == "group":
            chats = chats.filter(type=Chat.GROUP)
        elif tab == "private":
            chats = chats.filter(type=Chat.PRIVATE)
        elif tab == "unread":
            # Chats with messages after last_read_at
            chats = chats.filter(
                members__user=request.user,
                messages__created_at__gt=F("members__last_read_at")
            ).distinct()

        chat_list = []

        for chat in chats:
            # Determine other user for private chats
            other_member = None
            other_user = None
            if chat.type == Chat.PRIVATE:
                other_member = chat.members.exclude(user=request.user).first()
                other_user = other_member.user if other_member else None

            # Count unread messages
            unread_count = 0
            member_obj = chat.members.filter(user=request.user).first()
            if member_obj:
                if member_obj.last_read_at:
                    unread_count = chat.messages.filter(
                        created_at__gt=member_obj.last_read_at
                    ).exclude(sender=request.user).count()
                else:
                    unread_count = chat.messages.exclude(sender=request.user).count()

            # Determine display_name
            if chat.type == Chat.GROUP:
                display_name = chat.title or "Group Chat"
            elif chat.type == Chat.PRIVATE and other_user:
                contact_obj = request.user.contacts.filter(contact_user=other_user).first()
                if contact_obj and contact_obj.display_name:
                    display_name = contact_obj.display_name
                else:
                    display_name = str(other_user.phone_number) if other_user.phone_number else other_user.email
            else:
                display_name = chat.title or "Unknown"

            # Avatar
            avatar_url = chat.avatar.url if chat.type == Chat.GROUP else (
                other_user.avatar.url if other_user and getattr(other_user, "avatar", None) else None
            )

            # Last message
            last_message_obj = chat.messages.order_by("-created_at").first()
            last_message = last_message_obj.content if last_message_obj else None

            chat_list.append({
                "id": str(chat.id),
                "type": chat.type,
                "display_name": display_name,
                "avatar_url": avatar_url,
                "last_message": last_message,
                "created_at": chat.created_at,
                "unread_count": unread_count,
            })

        return Response(chat_list)

# class CreatePrivateChatView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):








        
      
        
#         other_user_id = request.data.get("user_id")
#         other_user = get_object_or_404(User, id=other_user_id)

#         chat = Chat.objects.filter(
#             type=Chat.PRIVATE,
#             members_user=request.user

#         ).filter(
#             members_user=other_user
#         ).first()

#         if not chat:
#             chat = Chat.objects.create(type=Chat.PRIVATE)
#             ChatMember.objects.create(chat=chat, user=request.user, role=ChatMember.MEMBER)
#             ChatMember.objects.create(chat=chat, user=other_user, role=ChatMember.MEMBER)
#         serializer = ChatSerializer(chat)
#         return Response(serializer.data, status=201)

# class CreatePrivateChatView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         phone_number = request.data.get("phone_number")
#         other_user = get_object_or_404(User, phone_number=phone_number)

#         chat = Chat.objects.filter(
#             type=Chat.PRIVATE,
#             members__user=request.user
#         ).filter(
#             members__user=other_user
#         ).first()

#         if not chat:
#             chat = Chat.objects.create(type=Chat.PRIVATE)
#             ChatMember.objects.create(chat=chat, user=request.user, role=ChatMember.MEMBER)
#             ChatMember.objects.create(chat=chat, user=other_user, role=ChatMember.MEMBER)

#         serializer = ChatSerializer(chat)
#         return Response(serializer.data, status=201)

class CreatePrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic  # ensure atomicity
    def post(self, request):
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response({"error": "Phone number is required"}, status=400)

        other_user = get_object_or_404(User, phone_number=phone_number)

        # Check if a private chat between these two users already exists
        chat = Chat.objects.filter(
            type=Chat.PRIVATE,
            members__user=request.user
        ).filter(
            members__user=other_user
        ).distinct().first()

        if not chat:
            # Create new private chat
            chat = Chat.objects.create(type=Chat.PRIVATE)
            ChatMember.objects.bulk_create([
                ChatMember(chat=chat, user=request.user, role=ChatMember.MEMBER),
                ChatMember(chat=chat, user=other_user, role=ChatMember.MEMBER)
            ])
        else:
            # Safety: ensure both members exist
            if not chat.members.filter(user=request.user).exists():
                ChatMember.objects.create(chat=chat, user=request.user, role=ChatMember.MEMBER)
            if not chat.members.filter(user=other_user).exists():
                ChatMember.objects.create(chat=chat, user=other_user, role=ChatMember.MEMBER)

        serializer = ChatSerializer(chat, context={"request": request})
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