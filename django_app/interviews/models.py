import random
import string

from django.conf import settings
from django.db import models


def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Room(models.Model):
    room_name = models.CharField(max_length=100)
    room_code = models.CharField(max_length=10, unique=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="rooms_created", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        "questions.Question", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_code:
            code = generate_room_code()
            while Room.objects.filter(room_code=code).exists():
                code = generate_room_code()
            self.room_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room_name} ({self.room_code})"
