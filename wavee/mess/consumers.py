# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        # -----------------------
        # 1. MESSAGE
        # -----------------------
        if event_type == "message":
            msg = await self.save_message(data["content"])

            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "broadcast_message",
                    "message": data["content"],
                    "sender_id": str(self.user.id),
                    "message_id": str(msg.id),
                    "timestamp": msg.timestamp.isoformat(),
                }
            )

        # -----------------------
        # 2. TYPING INDICATOR
        # -----------------------
        elif event_type == "typing":
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "typing_event",
                    "user_id": str(self.user.id),
                }
            )

        # -----------------------
        # 3. READ RECEIPT
        # -----------------------
        elif event_type == "read":
            message_id = data["message_id"]
            await self.mark_read(message_id)

            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "read_event",
                    "message_id": message_id,
                    "user_id": str(self.user.id),
                }
            )

    # -----------------------
    # EVENTS TO FRONTEND
    # -----------------------

    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"]
        }))

    async def read_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "read",
            "message_id": event["message_id"],
            "user_id": event["user_id"]
        }))

    # -----------------------
    # DB HELPERS
    # -----------------------

    async def save_message(self, content):
        return await Message.objects.acreate(
            conversation_id=self.conversation_id,
            sender=self.user,
            content=content,
            timestamp=timezone.now(),
            status="sent"
        )

    async def mark_read(self, message_id):
        await Message.objects.filter(id=message_id).aupdate(status="read")