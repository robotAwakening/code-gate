import unittest

from code_gate.challenges import (
    Challenge,
    all_challenges,
    check_answer,
    difficulty_for_attempts,
    get_challenge,
)


class DifficultyForAttemptsTests(unittest.TestCase):
    def test_zero_attempts_gives_easy(self) -> None:
        self.assertEqual(difficulty_for_attempts(0), 1)

    def test_one_attempt_gives_medium(self) -> None:
        self.assertEqual(difficulty_for_attempts(1), 2)

    def test_two_attempts_gives_medium(self) -> None:
        self.assertEqual(difficulty_for_attempts(2), 2)

    def test_three_or_more_attempts_gives_hard(self) -> None:
        self.assertEqual(difficulty_for_attempts(3), 3)
        self.assertEqual(difficulty_for_attempts(10), 3)

    def test_negative_attempts_give_easy(self) -> None:
        self.assertEqual(difficulty_for_attempts(-1), 1)


class ChallengeDataTests(unittest.TestCase):
    def test_all_challenges_have_required_fields(self) -> None:
        for c in all_challenges():
            self.assertIn("id",         c)
            self.assertIn("category",   c)
            self.assertIn("question",   c)
            self.assertIn("answer",     c)
            self.assertIn("difficulty", c)
            self.assertIn(c["difficulty"], {1, 2, 3})
            self.assertIn(c["category"], {"math", "coding", "logic"})

    def test_all_challenge_ids_are_unique(self) -> None:
        ids = [c["id"] for c in all_challenges()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_coverage_all_difficulties_present(self) -> None:
        diffs = {c["difficulty"] for c in all_challenges()}
        self.assertEqual(diffs, {1, 2, 3})

    def test_coverage_all_categories_present(self) -> None:
        cats = {c["category"] for c in all_challenges()}
        self.assertGreaterEqual(cats, {"math", "coding", "logic"})

    def test_options_when_present_have_four_items(self) -> None:
        for c in all_challenges():
            if c["options"] is not None:
                self.assertEqual(len(c["options"]), 4, msg=f"Challenge {c['id']} has wrong option count")

    def test_options_when_present_include_the_correct_answer(self) -> None:
        for c in all_challenges():
            if c["options"] is not None:
                self.assertIn(
                    c["answer"],
                    c["options"],
                    msg=f"Challenge {c['id']}: answer not in options",
                )


class CheckAnswerTests(unittest.TestCase):
    def _make_challenge(self, answer: str) -> Challenge:
        return {
            "id": 99,
            "category": "math",
            "question": "Dummy?",
            "answer": answer,
            "options": None,
            "difficulty": 1,
        }

    def test_exact_match_returns_true(self) -> None:
        c = self._make_challenge("42")
        self.assertTrue(check_answer(c, "42"))

    def test_case_insensitive_match(self) -> None:
        c = self._make_challenge("def")
        self.assertTrue(check_answer(c, "DEF"))
        self.assertTrue(check_answer(c, "Def"))

    def test_whitespace_stripped(self) -> None:
        c = self._make_challenge("Stack")
        self.assertTrue(check_answer(c, "  Stack  "))

    def test_wrong_answer_returns_false(self) -> None:
        c = self._make_challenge("56")
        self.assertFalse(check_answer(c, "57"))

    def test_empty_answer_returns_false(self) -> None:
        c = self._make_challenge("56")
        self.assertFalse(check_answer(c, ""))


class GetChallengeTests(unittest.TestCase):
    def test_returns_easy_for_zero_attempts(self) -> None:
        c = get_challenge(attempts_today=0)
        self.assertEqual(c["difficulty"], 1)

    def test_returns_medium_for_two_attempts(self) -> None:
        c = get_challenge(attempts_today=2)
        self.assertEqual(c["difficulty"], 2)

    def test_returns_hard_for_four_attempts(self) -> None:
        c = get_challenge(attempts_today=4)
        self.assertEqual(c["difficulty"], 3)

    def test_exclude_ids_are_respected(self) -> None:
        all_easy = [c["id"] for c in all_challenges() if c["difficulty"] == 1]
        # Exclude all but one easy challenge
        exclude = all_easy[:-1]
        c = get_challenge(attempts_today=0, exclude_ids=exclude)
        self.assertEqual(c["id"], all_easy[-1])

    def test_returns_a_challenge_dict(self) -> None:
        c = get_challenge(attempts_today=0)
        self.assertIsInstance(c, dict)
        self.assertIn("question", c)


if __name__ == "__main__":
    unittest.main()
