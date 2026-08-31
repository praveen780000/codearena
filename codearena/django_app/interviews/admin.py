from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'room_code', 'created_by', 'question', 'created_at')
