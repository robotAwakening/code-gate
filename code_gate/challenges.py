"""Challenge bank for the code-gate learning engine.

Challenges are grouped into three difficulty tiers:
  1 = easy   (first unlock attempt of the day)
  2 = medium (2–3 attempts today)
  3 = hard   (4+ attempts today)

Each challenge has:
  id        – unique integer
  category  – "math" | "coding" | "logic"
  question  – text shown to the user
  answer    – canonical correct answer (case-insensitive, stripped)
  options   – optional list of 4 strings for multiple-choice display
  difficulty – 1 | 2 | 3
"""
from __future__ import annotations

import random
from typing import TypedDict


class Challenge(TypedDict):
    id: int
    category: str
    question: str
    answer: str
    options: list[str] | None
    difficulty: int


# ---------------------------------------------------------------------------
# Challenge bank
# ---------------------------------------------------------------------------

_CHALLENGES: list[Challenge] = [
    # --- Math / easy ---
    {
        "id": 1,
        "category": "math",
        "question": "What is 7 × 8?",
        "answer": "56",
        "options": ["48", "54", "56", "64"],
        "difficulty": 1,
    },
    {
        "id": 2,
        "category": "math",
        "question": "What is 15 + 27?",
        "answer": "42",
        "options": ["40", "41", "42", "43"],
        "difficulty": 1,
    },
    {
        "id": 3,
        "category": "math",
        "question": "What is 144 ÷ 12?",
        "answer": "12",
        "options": ["11", "12", "13", "14"],
        "difficulty": 1,
    },
    {
        "id": 4,
        "category": "math",
        "question": "What is 9²?",
        "answer": "81",
        "options": ["72", "81", "90", "99"],
        "difficulty": 1,
    },
    # --- Coding / easy ---
    {
        "id": 5,
        "category": "coding",
        "question": "In Python, which keyword is used to define a function?",
        "answer": "def",
        "options": ["fun", "function", "define", "def"],
        "difficulty": 1,
    },
    {
        "id": 6,
        "category": "coding",
        "question": "What does HTML stand for?",
        "answer": "HyperText Markup Language",
        "options": [
            "HyperText Markup Language",
            "HighText Machine Language",
            "Hyper Transfer Markup Language",
            "HyperText Modern Language",
        ],
        "difficulty": 1,
    },
    # --- Logic / easy ---
    {
        "id": 7,
        "category": "logic",
        "question": "If you have 3 apples and give away 1, how many do you have left?",
        "answer": "2",
        "options": ["1", "2", "3", "4"],
        "difficulty": 1,
    },
    {
        "id": 8,
        "category": "logic",
        "question": "A rooster lays an egg on the peak of a roof. Which way does the egg roll?",
        "answer": "Roosters do not lay eggs",
        "options": [
            "Left",
            "Right",
            "Straight down",
            "Roosters do not lay eggs",
        ],
        "difficulty": 1,
    },
    # --- Math / medium ---
    {
        "id": 9,
        "category": "math",
        "question": "What is the square root of 196?",
        "answer": "14",
        "options": ["12", "13", "14", "15"],
        "difficulty": 2,
    },
    {
        "id": 10,
        "category": "math",
        "question": "What is 17 × 13?",
        "answer": "221",
        "options": ["211", "221", "231", "241"],
        "difficulty": 2,
    },
    {
        "id": 11,
        "category": "math",
        "question": "What is 20% of 350?",
        "answer": "70",
        "options": ["60", "65", "70", "75"],
        "difficulty": 2,
    },
    # --- Coding / medium ---
    {
        "id": 12,
        "category": "coding",
        "question": "Which data structure uses LIFO (Last-In First-Out) ordering?",
        "answer": "Stack",
        "options": ["Queue", "Stack", "Heap", "Tree"],
        "difficulty": 2,
    },
    {
        "id": 13,
        "category": "coding",
        "question": "What is the time complexity of binary search on a sorted array?",
        "answer": "O(log n)",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
        "difficulty": 2,
    },
    {
        "id": 14,
        "category": "coding",
        "question": "In Python, what does `len([1, 2, 3])` return?",
        "answer": "3",
        "options": ["2", "3", "4", "None"],
        "difficulty": 2,
    },
    # --- Logic / medium ---
    {
        "id": 15,
        "category": "logic",
        "question": "A is taller than B. B is taller than C. Who is the shortest?",
        "answer": "C",
        "options": ["A", "B", "C", "Cannot be determined"],
        "difficulty": 2,
    },
    # --- Math / hard ---
    {
        "id": 16,
        "category": "math",
        "question": "What is the value of 2¹⁰?",
        "answer": "1024",
        "options": ["512", "1000", "1024", "2048"],
        "difficulty": 3,
    },
    {
        "id": 17,
        "category": "math",
        "question": "If f(x) = 3x² – 2x + 1, what is f(3)?",
        "answer": "22",
        "options": ["20", "22", "24", "26"],
        "difficulty": 3,
    },
    # --- Coding / hard ---
    {
        "id": 18,
        "category": "coding",
        "question": "What sorting algorithm has an average time complexity of O(n log n) and worst-case O(n²)?",
        "answer": "Quick Sort",
        "options": ["Merge Sort", "Heap Sort", "Quick Sort", "Bubble Sort"],
        "difficulty": 3,
    },
    {
        "id": 19,
        "category": "coding",
        "question": "In a binary tree, what is the maximum number of nodes at depth d?",
        "answer": "2^d",
        "options": ["d", "2d", "2^d", "d²"],
        "difficulty": 3,
    },
    {
        "id": 20,
        "category": "coding",
        "question": "Which design pattern ensures a class has only one instance?",
        "answer": "Singleton",
        "options": ["Factory", "Singleton", "Observer", "Strategy"],
        "difficulty": 3,
    },
    # --- Logic / hard ---
    {
        "id": 21,
        "category": "logic",
        "question": "You have two ropes, each burns in exactly 60 minutes (non-uniformly). How do you measure 45 minutes?",
        "answer": "Light rope 1 from both ends and rope 2 from one end simultaneously; when rope 1 burns out (30 min), light rope 2's other end",
        "options": [
            "Light rope 1 from both ends and rope 2 from one end simultaneously; when rope 1 burns out (30 min), light rope 2's other end",
            "Cut each rope in half and burn one half of each",
            "Burn rope 1 fully, then burn rope 2",
            "Light both ropes from both ends at the same time",
        ],
        "difficulty": 3,
    },
]


def difficulty_for_attempts(attempts_today: int) -> int:
    """Map today's unlock attempt count to a difficulty tier (1–3)."""
    if attempts_today <= 0:
        return 1
    if attempts_today <= 2:
        return 2
    return 3


def get_challenge(attempts_today: int, exclude_ids: list[int] | None = None) -> Challenge:
    """Return a random challenge at the appropriate difficulty level.

    Falls back to the next-lower tier if none are available at the target tier.
    """
    target = difficulty_for_attempts(attempts_today)
    exclude = set(exclude_ids or [])

    for tier in (target, max(target - 1, 1), 1):
        candidates = [
            c for c in _CHALLENGES if c["difficulty"] == tier and c["id"] not in exclude
        ]
        if candidates:
            return random.choice(candidates)

    # absolute fallback – return any challenge
    return random.choice(_CHALLENGES)


def check_answer(challenge: Challenge, user_answer: str) -> bool:
    """Return True if *user_answer* matches the canonical answer (case-insensitive)."""
    return user_answer.strip().lower() == challenge["answer"].strip().lower()


def all_challenges() -> list[Challenge]:
    """Return a copy of the full challenge list (for testing/inspection)."""
    return list(_CHALLENGES)
