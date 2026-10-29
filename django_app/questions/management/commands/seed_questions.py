from django.core.management.base import BaseCommand
from questions.models import Question

QUESTIONS = [
    {
        "title": "Sum of Two Numbers",
        "description": "Read two space-separated integers from stdin and print their sum.",
        "difficulty": "easy",
        "starter_code": "a, b = map(int, input().split())\nprint(a + b)\n",
        "sample_input": "3 5",
        "sample_output": "8",
    },
    {
        "title": "FizzBuzz",
        "description": (
            "Read an integer n from stdin. For each number from 1 to n, print 'Fizz' if divisible "
            "by 3, 'Buzz' if divisible by 5, 'FizzBuzz' if divisible by both, otherwise the number."
        ),
        "difficulty": "easy",
        "starter_code": (
            "n = int(input())\n"
            "for i in range(1, n + 1):\n"
            "    if i % 15 == 0:\n"
            "        print('FizzBuzz')\n"
            "    elif i % 3 == 0:\n"
            "        print('Fizz')\n"
            "    elif i % 5 == 0:\n"
            "        print('Buzz')\n"
            "    else:\n"
            "        print(i)\n"
        ),
        "sample_input": "5",
        "sample_output": "1\n2\nFizz\n4\nBuzz",
    },
    {
        "title": "Palindrome Check",
        "description": "Read a string from stdin and print True if it's a palindrome, else False.",
        "difficulty": "medium",
        "starter_code": "s = input().strip()\nprint(s == s[::-1])\n",
        "sample_input": "madam",
        "sample_output": "True",
    },
    {
        "title": "Reverse Words in a Sentence",
        "description": "Read a sentence from stdin and print its words in reverse order, space-separated.",
        "difficulty": "medium",
        "starter_code": "s = input().strip()\nprint(' '.join(s.split()[::-1]))\n",
        "sample_input": "hello world from codearena",
        "sample_output": "codearena from world hello",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample coding questions for demo purposes."

    def handle(self, *args, **options):
        for q in QUESTIONS:
            Question.objects.get_or_create(title=q["title"], defaults=q)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(QUESTIONS)} question(s)."))
