import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Room


class RoomConsumer(AsyncWebsocketConsumer):
    """
    One group per interview room (keyed by room_code). Broadcasts:
      - code_update: live sync of the shared editor's contents
      - chat_message: room chat
      - user_joined / user_left: presence, for the online-count badge
    """

    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"].upper()
        self.room_group_name = f"room_{self.room_code}"
        self.user = self.scope.get("user")

        # Reject anonymous users and unknown rooms before joining the group.
        if self.user is None or not self.user.is_authenticated:
            await self.close()
            return

        room_exists = await self._room_exists()
        if not room_exists:
            await self.close()
            return

        await self._add_participant()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user_joined", "username": self.user.username},
        )

    async def disconnect(self, close_code):
        if not hasattr(self, "room_group_name"):
            return

        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_left", "username": self.user.username},
            )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (TypeError, ValueError):
            return

        if data.get("type") == "chat":
            message = (data.get("message") or "").strip()
            if not message:
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                },
            )
            return

        # Anything else is treated as a live code update from the shared editor.
        code = data.get("code", "")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "code_update",
                "code": code,
                # so the sender doesn't get its own keystrokes echoed back
                "sender_channel": self.channel_name,
            },
        )

    # --- group event handlers (name must match the "type" key above) ----

    async def code_update(self, event):
        if event.get("sender_channel") == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            "action": "code_update",
            "code": event["code"],
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "action": "chat",
            "message": event["message"],
            "username": event["username"],
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            "action": "user_joined",
            "username": event["username"],
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            "action": "user_left",
            "username": event["username"],
        }))

    # --- db helpers -------------------------------------------------------

    @database_sync_to_async
    def _room_exists(self):
        return Room.objects.filter(room_code=self.room_code).exists()

    @database_sync_to_async
    def _add_participant(self):
        room = Room.objects.filter(room_code=self.room_code).first()
        if room:
            room.participants.add(self.user)
