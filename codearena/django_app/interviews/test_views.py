from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import User
from questions.models import Question
from submissions.models import Submission
from .models import Room


class RoomDetailTests(TestCase):
    def setUp(self):
        self.interviewer = User.objects.create_user(
            username="interviewer", password="password", role="interviewer"
        )
        self.student = User.objects.create_user(
            username="student", password="password", role="student"
        )
        self.question = Question.objects.create(
            title="Question", description="Description", sample_output="answer"
        )
        self.room = Room.objects.create(
            room_name="Room", created_by=self.interviewer, question=self.question
        )
        self.url = reverse("room_detail", args=[self.room.room_code])

    def test_interviewer_cannot_submit_a_solution(self):
        self.client.force_login(self.interviewer)

        response = self.client.post(self.url, {"code": "print('answer')"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.url)
        self.assertFalse(Submission.objects.exists())

    @patch("interviews.views.judge_code")
    def test_student_submission_is_saved(self, judge_code):
        judge_code.return_value = {
            "output": "answer\n",
            "status": "Passed",
            "similarity_score": 0.0,
            "most_similar_user": "",
        }
        self.client.force_login(self.student)

        response = self.client.post(self.url, {"code": "print('answer')"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.url)
        submission = Submission.objects.get()
        self.assertEqual(submission.user, self.student)
        self.assertEqual(submission.room, self.room)
        judge_code.assert_called_once()

    @patch("interviews.views.render")
    def test_creator_can_review_candidate_submissions(self, render):
        Submission.objects.create(
            user=self.student, question=self.question, room=self.room, code="print('answer')"
        )
        render.return_value = HttpResponse()
        request = RequestFactory().get(self.url)
        request.user = self.interviewer

        from .views import room_detail_view

        room_detail_view(request, self.room.room_code)

        self.assertEqual(list(render.call_args.args[2]["submissions"]), [Submission.objects.get(user=self.student)])
