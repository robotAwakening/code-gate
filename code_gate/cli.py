from __future__ import annotations

import argparse
from pathlib import Path

from .gate import GateState, load_state, save_state

DEFAULT_STATE_PATH = Path.home() / ".code_gate" / "state.json"

QUESTION = "What is 2 + 2?"
ANSWER = "4"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="code-gate local CLI prototype")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE_PATH,
        help=f"State file path (default: {DEFAULT_STATE_PATH})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    check_app = subparsers.add_parser("check-app", help="Check whether an app package is blocked")
    check_app.add_argument("package_name")

    check_url = subparsers.add_parser("check-url", help="Check whether a URL/host is blocked")
    check_url.add_argument("url_or_host")

    subparsers.add_parser("status", help="Show current gate state")
    subparsers.add_parser("solve", help="Solve one challenge to unlock")
    subparsers.add_parser("reset", help="Reset local state")

    return parser


def _print_status(state: GateState) -> None:
    print(f"required_challenges={state.required_challenges}")
    print(f"solved_challenges={state.solved_challenges}")
    print(f"unlock_attempts_today={state.unlock_attempts_today}")
    print(f"is_unlocked={state.is_unlocked}")


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    state = load_state(args.state_file)

    if args.command == "status":
        _print_status(state)
        return 0

    if args.command == "reset":
        state = GateState()
        save_state(args.state_file, state)
        print(f"State reset at {args.state_file}")
        return 0

    if args.command == "check-app":
        blocked = state.is_target_blocked(args.package_name, "app")
        print("BLOCKED" if blocked else "ALLOWED")
        return 0

    if args.command == "check-url":
        blocked = state.is_target_blocked(args.url_or_host, "url")
        print("BLOCKED" if blocked else "ALLOWED")
        return 0

    if args.command == "solve":
        print(f"Challenge: {QUESTION}")
        user_answer = input("Answer: ").strip()
        solved = user_answer == ANSWER
        unlocked = state.register_unlock_attempt(solved=solved)
        save_state(args.state_file, state)
        if solved:
            print("Correct answer.")
        else:
            print("Wrong answer.")
        print("UNLOCKED" if unlocked else "STILL_BLOCKED")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
