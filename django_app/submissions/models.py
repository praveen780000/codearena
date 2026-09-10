from django.conf import settings
from django.db import models


class Submission(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Passed", "Passed"),
        ("Failed", "Failed"),
        ("Error", "Error"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE)
    question = models.ForeignKey("questions.Question", related_name="submissions", on_delete=models.CASCADE)
    room = models.ForeignKey(
        "interviews.Room", null=True, blank=True, related_name="submissions", on_delete=models.SET_NULL
    )
    code = models.TextField()
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    similarity_score = models.FloatField(default=0.0)
    most_similar_user = models.CharField(max_length=150, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user} - {self.question} - {self.status}"
