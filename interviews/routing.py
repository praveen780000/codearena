from django.urls import re_path

from .consumers import RoomConsumer

websocket_urlpatterns = [
    re_path(r"^ws/room/(?P<room_code>[A-Za-z0-9]+)/$", RoomConsumer.as_asgi()),
]
