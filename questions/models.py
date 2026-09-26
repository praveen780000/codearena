from django.db import models


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="easy")
    starter_code = models.TextField(blank=True, default="# Write your solution below\n")
    sample_input = models.TextField(blank=True, help_text="Fed to the program via stdin")
    sample_output = models.TextField(
        blank=True, help_text="Expected stdout (compared after trimming whitespace)"
    )

    def __str__(self):
        return self.title
