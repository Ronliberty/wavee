import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, ChatMember
from mess.models import  Message, Attachment

from mess.serializers import MessageSerializer
from users.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        is_member = await database_sync_to_async(self.is_chat_member)(user, self.chat_id)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")
        user = self.scope["user"]

        if event_type == "message":
            content = data.get("content", "")
            attachments = data.get("attachments", [])

            message = await database_sync_to_async(self.create_message)(user, content, attachments)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": MessageSerializer(message).data
                }
            )
        elif event_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing",
                    "user_id": user.id,
                    "is_typing": data.get("is_typing", False)
                }
            )
        elif event_type == "read":
            message_id = data.get("message_id")
            await database_sync_to_async(self.mark_read)(message_id, user)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_read",
                    "message_id": message_id,
                    "user_id": user.id
                }
            )

    async def chat_message(self, event):
        
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event.get("message")
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"],
            "is_typing": event["is_typing"]
        }))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            "type": "read",
            "message_id": event.get("message_id"),
            "user_id": event.get("user_id")
        }))

    def is_chat_member(self, user, chat_id):
        return ChatMember.objects.filter(chat_id=chat_id, user=user).exists()

    def create_message(self, sender, content, attachments):
        chat = Chat.objects.get(id=self.chat_id)
        message = Message.objects.create(
            chat=chat,
            sender=sender,
            content=content,
            type="text"
        )

        for att in attachments:
            Attachment.objects.create(
                message=message,
                file=att.get("url"),
                file_type=att.get("file_type", "application/octet-stream")
            )

        return message

    def mark_read(self, message_id, user):
        message = Message.objects.get(id=message_id)
        message.read_by.add(user)
        message.delivered_to.add(user)
        message.save()
