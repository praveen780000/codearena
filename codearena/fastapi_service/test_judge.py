import unittest

from judge import compute_similarity, judge_submission


class JudgeSubmissionTests(unittest.TestCase):
    def test_marks_matching_output_as_passed(self):
        result = judge_submission("print(input())", "hello\n", "hello")

        self.assertEqual(result, {"output": "hello\n", "status": "Passed"})

    def test_marks_mismatched_output_as_failed(self):
        result = judge_submission("print('actual')", expected_output="expected")

        self.assertEqual(result["status"], "Failed")

    def test_marks_invalid_python_as_error(self):
        result = judge_submission("def broken(:\n")

        self.assertEqual(result["status"], "Error")
        self.assertIn("SyntaxError", result["output"])


class SimilarityTests(unittest.TestCase):
    def test_reports_highest_match_and_ignores_empty_code(self):
        result = compute_similarity(
            "print('same')",
            [
                {"username": "empty", "code": "   "},
                {"username": "different", "code": "print('different')"},
                {"username": "match", "code": "print('same')"},
            ],
        )

        self.assertEqual(result, {"similarity_score": 100.0, "most_similar_user": "match"})
