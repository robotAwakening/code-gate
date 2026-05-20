from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .blocking_targets import is_blocked_app, is_blocked_url

TargetType = Literal["app", "url"]


@dataclass
class GateState:
    required_challenges: int = 1
    solved_challenges: int = 0
    unlock_attempts_today: int = 0

    @property
    def is_unlocked(self) -> bool:
        return self.solved_challenges >= self.required_challenges

    def is_target_blocked(self, target: str, target_type: TargetType) -> bool:
        if self.is_unlocked:
            return False
        if target_type == "app":
            return is_blocked_app(target)
        if target_type == "url":
            return is_blocked_url(target)
        raise ValueError(f"Unsupported target_type: {target_type}")

    def register_unlock_attempt(self, solved: bool) -> bool:
        self.unlock_attempts_today += 1
        if solved:
            self.solved_challenges += 1
        return self.is_unlocked


def load_state(path: str | Path) -> GateState:
    state_path = Path(path)
    if not state_path.exists():
        return GateState()

    data = json.loads(state_path.read_text(encoding="utf-8"))
    return GateState(
        required_challenges=int(data.get("required_challenges", 1)),
        solved_challenges=int(data.get("solved_challenges", 0)),
        unlock_attempts_today=int(data.get("unlock_attempts_today", 0)),
    )


def save_state(path: str | Path, state: GateState) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
