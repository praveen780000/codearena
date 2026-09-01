from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .services import JudgeServiceError, judge_code


class JudgeServiceTests(SimpleTestCase):
    @patch("submissions.services.requests.post")
    def test_rejects_incomplete_judge_response(self, post):
        response = Mock()
        response.json.return_value = {"status": "Passed"}
        post.return_value = response

        with self.assertRaisesRegex(JudgeServiceError, "incomplete result"):
            judge_code("print('ok')", "", "", [])

    @patch("submissions.services.requests.post")
    def test_rejects_invalid_judge_status(self, post):
        response = Mock()
        response.json.return_value = {
            "output": "",
            "status": "Pending",
            "similarity_score": 0,
            "most_similar_user": "",
        }
        post.return_value = response

        with self.assertRaisesRegex(JudgeServiceError, "invalid submission status"):
            judge_code("print('ok')", "", "", [])
