
import json
import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Room


class RoomConsumer(AsyncWebsocketConsumer):


    # room_code -> {username: set(channel_names)}
    room_presence = {}
    presence_lock = asyncio.Lock()

    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"][
            "room_code"
        ].upper()

        self.room_group_name = f"room_{self.room_code}"
        self.user = self.scope.get("user")
        self.username = None
        self.registered = False

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        if not await self._room_exists():
            await self.close()
            return

        self.username = self.user.username

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

        # Register this WebSocket connection.
        async with self.presence_lock:
            users = self.room_presence.setdefault(self.room_code, {})
            connections = users.setdefault(self.username, set())
            was_online = bool(connections)
            connections.add(self.channel_name)
            self.registered = True
            online_count = len(users)


        await self._add_participant()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_update",
                "username": self.username,
                "online_count": online_count,
                "event": "joined" if not was_online else "connected",
            },
        )

    async def disconnect(self, close_code):
        if not hasattr(self, "room_group_name"):
            return

        if self.registered:
            async with self.presence_lock:
                users = self.room_presence.get(self.room_code, {})
                connections = users.get(self.username, set())

                connections.discard(self.channel_name)

                if not connections:
                    users.pop(self.username, None)

                if not users:
                    self.room_presence.pop(self.room_code, None)
                    online_count = 0
                else:
                    online_count = len(users)

                user_left = not connections

            if user_left:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "presence_update",
                        "username": self.username,
                        "online_count": online_count,
                        "event": "left",
                    },
                )

        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

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
                    "username": self.username,
                },
            )
            return

        if "code" in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "code_update",
                    "code": data["code"],
                    "sender_channel": self.channel_name,
                },
            )

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

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "presence_update",
            "username": event["username"],
            "online_count": event["online_count"],
            "event": event["event"],
        }))

    @database_sync_to_async
    def _room_exists(self):
        return Room.objects.filter(
            room_code=self.room_code
        ).exists()

    @database_sync_to_async
    def _add_participant(self):
        room = Room.objects.filter(
            room_code=self.room_code
        ).first()

        if room:
            room.participants.add(self.user)
