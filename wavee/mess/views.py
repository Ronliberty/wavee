from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Message, Attachment
from .serializers import MessageSerializer, CreateMessageSerializer
from chat.models import Chat
from django.shortcuts import get_object_or_404
from django.db import transaction


# class ListMessagesView(APIView):
#     permissions_classes = [permissions.IsAuthenticated]

#     def get(self, request, chat_id):
#         chat = get_object_or_404(Chat, id=chat_id)
#         if not chat.members.filter(user=request.user).exists():
#             return Response({"error": "Not a member of this chat"}, status=403)
#         messages = chat.messsages.all().order_by("created_at")
#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)
    
class ListMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        if not chat.members.filter(user=request.user).exists():
            return Response({"error": "Not a member of this chat"}, status=403)
        
        # Fixed typo here
        messages = chat.messages.all().order_by("created_at")
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)



# class SendMessageView(APIView):
#     permissions_classes = [permissions.IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         serializer = CreateMessageSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         chat = get_object_or_404(Chat, id=serializer.validated_data["chat"].id)

#         if not chat.members.filter(user=request.user).exists():
#             return Response({"error": "Not a mamber of this chat" }, status=403)
#         message = serializer.save(sender=request.user)

#         files = request.FILES.getlist("attachments")
#         for f in files:
#             Attachment.objects.create(
#                 message=message,
#                 file=f,
#                 file_type=f.content_type,
#                 file_size=f.size
#             )
#         return Response(MessageSerializer(message).data, status=201)
    

class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        data = request.data.copy()  # Work with a mutable copy

        # Ensure chat ID is passed correctly
        chat_id = data.get("chat")
        if not chat_id:
            return Response({"error": "Chat ID is required"}, status=400)

        chat = get_object_or_404(Chat, id=chat_id)

        # Check membership
        if not chat.members.filter(user=request.user).exists():
            return Response({"error": "Not a member of this chat"}, status=403)

        # Serialize the message
        serializer = CreateMessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user)

        # Handle attachments (if any)
        files = request.FILES.getlist("attachments")
        for f in files:
            Attachment.objects.create(
                message=message,
                file=f,
                file_type=f.content_type,
                file_size=f.size
            )

        return Response(MessageSerializer(message).data, status=201)

# class MarkMessageReadView(APIView):
#     permissions_classes = [permissions.IsAuthenticated]

#     def post(self, request, message_id):
#         message = get_object_or_404(Message, id=message_id)
#         if request.user not in message.chat.members.values_list("user", flat=True):
#             return Response({"error": "not amember"}, status=403)
#         message.read_by.add(request.user)
#         return Response({"message": "Marked as read"}, status=200)


from django.utils import timezone

class MarkMessageReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        if request.user not in message.chat.members.values_list("user", flat=True):
            return Response({"error": "not a member"}, status=403)
        
        message.read_by.add(request.user)
        
        # Update last_read_at on the member object
        member_obj = message.chat.members.filter(user=request.user).first()
        if member_obj:
            member_obj.last_read_at = timezone.now()
            member_obj.save()
        
        return Response({"message": "Marked as read"}, status=200)
