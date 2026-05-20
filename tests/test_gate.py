import tempfile
import unittest
from pathlib import Path

from code_gate.gate import GateState, load_state, save_state


class GateStateTests(unittest.TestCase):
    def test_target_is_blocked_until_unlock(self) -> None:
        state = GateState()
        self.assertTrue(state.is_target_blocked("com.google.android.youtube", "app"))
        self.assertTrue(state.is_target_blocked("https://youtube.com/watch?v=1", "url"))

        unlocked = state.register_unlock_attempt(solved=True)
        self.assertTrue(unlocked)
        self.assertFalse(state.is_target_blocked("com.google.android.youtube", "app"))
        self.assertFalse(state.is_target_blocked("https://youtube.com/watch?v=1", "url"))

    def test_wrong_answer_does_not_unlock(self) -> None:
        state = GateState()
        unlocked = state.register_unlock_attempt(solved=False)
        self.assertFalse(unlocked)
        self.assertEqual(state.solved_challenges, 0)
        self.assertEqual(state.unlock_attempts_today, 1)

    def test_state_persistence_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state = GateState(required_challenges=1, solved_challenges=1, unlock_attempts_today=3)
            save_state(state_path, state)

            loaded = load_state(state_path)
            self.assertEqual(loaded.required_challenges, 1)
            self.assertEqual(loaded.solved_challenges, 1)
            self.assertEqual(loaded.unlock_attempts_today, 3)
            self.assertTrue(loaded.is_unlocked)


if __name__ == "__main__":
    unittest.main()
