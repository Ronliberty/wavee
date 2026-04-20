# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import permissions, status
# from .models import Message, Attachment
# from .serializers import MessageSerializer, CreateMessageSerializer
# from chat.models import Chat
# from django.shortcuts import get_object_or_404
# from django.db import transaction

# from django.utils import timezone

# from rest_framework.pagination import PageNumberPagination


# # class ListMessagesView(APIView):
# #     permissions_classes = [permissions.IsAuthenticated]

# #     def get(self, request, chat_id):
# #         chat = get_object_or_404(Chat, id=chat_id)
# #         if not chat.members.filter(user=request.user).exists():
# #             return Response({"error": "Not a member of this chat"}, status=403)
# #         messages = chat.messsages.all().order_by("created_at")
# #         serializer = MessageSerializer(messages, many=True)
# #         return Response(serializer.data)

# class MessagePagination(PageNumberPagination):
#     page_size = 20  # load 20 messages at a time
#     page_size_query_param = "page_size"

# class ListMessagesView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, chat_id):
#         chat = get_object_or_404(Chat, id=chat_id)
#         if not chat.members.filter(user=request.user).exists():
#             return Response({"error": "Not a member of this chat"}, status=403)

#         # Fixed typo here
#         messages = chat.messages.all().order_by("created_at")
#         paginator = MessagePagination()
#         result_page = paginator.paginate_queryset(messages, request)

#         serializer = MessageSerializer(messages, many=True, context={"request": request})
#         return paginator.get_paginated_response(serializer.data)



# # class SendMessageView(APIView):
# #     permissions_classes = [permissions.IsAuthenticated]

# #     @transaction.atomic
# #     def post(self, request):
# #         serializer = CreateMessageSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         chat = get_object_or_404(Chat, id=serializer.validated_data["chat"].id)

# #         if not chat.members.filter(user=request.user).exists():
# #             return Response({"error": "Not a mamber of this chat" }, status=403)
# #         message = serializer.save(sender=request.user)

# #         files = request.FILES.getlist("attachments")
# #         for f in files:
# #             Attachment.objects.create(
# #                 message=message,
# #                 file=f,
# #                 file_type=f.content_type,
# #                 file_size=f.size
# #             )
# #         return Response(MessageSerializer(message).data, status=201)


# class SendMessageView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         data = request.data.copy()  # Work with a mutable copy

#         # Ensure chat ID is passed correctly
#         chat_id = data.get("chat")
#         if not chat_id:
#             return Response({"error": "Chat ID is required"}, status=400)

#         chat = get_object_or_404(Chat, id=chat_id)

#         # Check membership
#         if not chat.members.filter(user=request.user).exists():
#             return Response({"error": "Not a member of this chat"}, status=403)

#         # Serialize the message
#         serializer = CreateMessageSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         message = serializer.save(sender=request.user)

#         # Handle attachments (if any)
#         files = request.FILES.getlist("attachments")
#         for f in files:
#             Attachment.objects.create(
#                 message=message,
#                 file=f,
#                 file_type=f.content_type,
#                 file_size=f.size
#             )

#         return Response(MessageSerializer(message).data, status=201)

# # class MarkMessageReadView(APIView):
# #     permissions_classes = [permissions.IsAuthenticated]

# #     def post(self, request, message_id):
# #         message = get_object_or_404(Message, id=message_id)
# #         if request.user not in message.chat.members.values_list("user", flat=True):
# #             return Response({"error": "not amember"}, status=403)
# #         message.read_by.add(request.user)
# #         return Response({"message": "Marked as read"}, status=200)



# # class MarkMessageReadView(APIView):
# #     permission_classes = [permissions.IsAuthenticated]

# #     def post(self, request, message_id):
# #         message = get_object_or_404(Message, id=message_id)
# #         if request.user not in message.chat.members.values_list("user", flat=True):
# #             return Response({"error": "not a member"}, status=403)

# #         message.read_by.add(request.user)

# #         # Update last_read_at on the member object
# #         member_obj = message.chat.members.filter(user=request.user).first()
# #         if member_obj:
# #             member_obj.last_read_at = timezone.now()
# #             member_obj.save()

# #         return Response({"message": "Marked as read"}, status=200)

# # class MarkMessageReadView(APIView):
# #     permission_classes = [permissions.IsAuthenticated]

# #     def post(self, request, message_id):


# #         message = get_object_or_404(Message, id=message_id)

# #         # Only allow marking read if request.user is NOT the sender
# #         if message.sender == request.user:
# #             return Response({"error": "Sender cannot mark their own message as read"}, status=403)

# #         # Ensure the user is a member of the chat
# #         if request.user not in message.chat.members.values_list("user", flat=True):
# #             return Response({"error": "Not a member of this chat"}, status=403)

# #         # Mark message as read
# #         message.read_by.add(request.user)

# #         # Update last_read_at for this chat member
# #         member_obj = message.chat.members.filter(user=request.user).first()
# #         if member_obj:
# #             member_obj.last_read_at = timezone.now()
# #             member_obj.save()

# #         return Response({"message": "Marked as read"}, status=200)


# class MarkMessageReadView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, message_id):
#         message = get_object_or_404(Message, id=message_id)

#         # Sender cannot mark own message
#         if message.sender_id == request.user.id:
#             return Response({"error": "Sender cannot mark their own message as read"}, status=403)

#         # Membership check
#         if request.user.id not in message.chat.members.values_list("user_id", flat=True):
#             return Response({"error": "Not a member of this chat"}, status=403)

#         # Mark as read
#         message.read_by.add(request.user)

#         # Update last_read_at for this member
#         member_obj = message.chat.members.filter(user=request.user).first()
#         if member_obj:
#             member_obj.last_read_at = timezone.now()
#             member_obj.save()

#         return Response({"message": "Marked as read"}, status=200)




from rest_framework import generics, permissions
from .models import Conversation, ConversationParticipant, Message
from .serializers import ConversationSerializer, MessageSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from contacts.models import Contact
User = get_user_model()










User = get_user_model()


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants__user=self.request.user
        ).select_related(
            "last_message"
        ).prefetch_related(
            "participants__user"
        ).distinct()

    def get_serializer_context(self):
        return {"request": self.request}



class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()

    def get_serializer_context(self):
        return {"request": self.request}







class StartConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contact_id = request.data.get("contact_id")

        if not contact_id:
            return Response(
                {"error": "contact_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_user = request.user

        # 1. Get contact (ONLY owned by current user)
        try:
            contact = Contact.objects.get(id=contact_id, owner=current_user)
        except Contact.DoesNotExist:
            return Response(
                {"error": "Contact not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Check if contact is a registered user
        if not contact.contact_user:
            return Response(
                {
                    "error": "User not on platform",
                    "can_invite": True,
                    "phone_number": str(contact.phone_number)
                },
                status=status.HTTP_404_NOT_FOUND
            )

        target_user = contact.contact_user

        if target_user == current_user:
            return Response(
                {"error": "You cannot start a conversation with yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Check existing 1-on-1 conversation
        existing_conversation = (
            Conversation.objects
            .filter(is_group=False)
            .annotate(num_participants=Count("participants"))
            .filter(num_participants=2)
            .filter(participants__user=current_user)
            .filter(participants__user=target_user)
            .first()
        )

        if existing_conversation:
            convo = existing_conversation
        else:
            # 4. Create new conversation
            convo = Conversation.objects.create(is_group=False)

            ConversationParticipant.objects.create(
                conversation=convo,
                user=current_user
            )

            ConversationParticipant.objects.create(
                conversation=convo,
                user=target_user
            )

        # 5. Return serialized conversation
        data = ConversationSerializer(
            convo,
            context={"request": request}
        ).data

        return Response(data, status=status.HTTP_200_OK)



class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]

        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by("created_at")

    def get_serializer_context(self):
        return {"request": self.request}








class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_id = request.data.get("receiver_id")
        content = request.data.get("content")

        if not receiver_id or not content:
            return Response({"error": "Missing data"}, status=400)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # 🔥 Find or create conversation
        conversation = Conversation.objects.filter(
            is_group=False,
            participants__user=sender
        ).filter(
            participants__user=receiver
        ).distinct().first()

        if not conversation:
            conversation = Conversation.objects.create(is_group=False)

            ConversationParticipant.objects.bulk_create([
                ConversationParticipant(conversation=conversation, user=sender),
                ConversationParticipant(conversation=conversation, user=receiver),
            ])

        # 🔥 Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content,
            status="sent"
        )

        # 🔥 Update last message
        conversation.last_message = message
        conversation.save()

        return Response({
            "message": MessageSerializer(message, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)


class MarkAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        user = request.user

        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        message.read_by.add(user)

        # Update participant last_read_at
        participant = ConversationParticipant.objects.filter(
            conversation=message.conversation,
            user=user
        ).first()

        if participant:
            participant.last_read_at = message.created_at
            participant.save()

        return Response({"status": "read"})