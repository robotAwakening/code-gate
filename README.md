# code-gate

Hybrid Android app concept that helps reduce excessive screentime by locking distracting apps/sites behind problem-solving.

## Problem this app solves

Users should be blocked from:
- YouTube app + YouTube in mobile browsers
- Instagram app + Instagram in mobile browsers

until they solve at least one challenge.

## MVP requirements

### 1) Blocking gate (Android)
- Block app launches for:
  - `com.google.android.youtube`
  - `com.instagram.android`
- Block browser access for:
  - `youtube.com`, `m.youtube.com`, `youtu.be`
  - `instagram.com`, `www.instagram.com`
- Keep blocked state active until one required challenge is solved.

### 2) Challenge engine
- Minimum one challenge required to unlock.
- Support difficulty progression:
  - Start with multiple-choice
  - Progress to fill-in / snippet-completion
  - Progress to full coding response
- Difficulty should adapt using:
  - Number of unlock attempts per day
  - Daily screentime on blocked targets

### 3) Progress and rewards
- Persist user progress locally:
  - Challenges solved
  - Daily streak
  - Time spent on blocked apps/sites
- Reward lower screentime and more solved challenges.
- Allow “challenge-only mode” (practice without unlocking intent).

### 4) Problem sources and categories
- Built-in categories:
  - Coding
  - Math
  - Sudoku/logic
  - Chess move puzzles
  - Science & nature
- External provider support via configurable API endpoint:
  - GET problems
  - Submit/validate answers
  - Category mapping

### 5) Monetization
- Preferred model:
  - Free app
  - Minimal ads
  - Optional donations/tips
- Secondary option:
  - Low-cost paid app listing

## Suggested technical architecture

- **UI layer**: Flutter or React Native
- **Blocking layer (Android native bridge)**:
  - Accessibility service for detecting blocked app foreground transitions
  - Usage Stats API for screentime metrics
  - Local VPN/DNS filtering for browser-domain blocking
- **Data layer**:
  - Local DB (SQLite) for progress/history
  - Provider abstraction for internal/external challenge APIs
- **Scoring layer**:
  - Rule engine to convert attempts + screentime into required difficulty

## Acceptance criteria

- Opening YouTube/Instagram app is intercepted and blocked while gate is active.
- Opening YouTube/Instagram URLs in browser is blocked while gate is active.
- Solving one required challenge immediately unlocks access.
- Higher daily attempts/screentime increase challenge difficulty.
- Progress remains after app restart.
- User can switch to challenge-only mode.
- Categories are selectable and external API can be configured.
- App supports ad-based free mode and optional donations.

## Current implementation progress

- Added a reusable blocking-target core in `code_gate/blocking_targets.py` for:
  - Android package blocking checks (`com.google.android.youtube`, `com.instagram.android`)
  - Browser host/URL blocking checks for YouTube and Instagram domains/subdomains
- Added focused tests in `tests/test_blocking_targets.py`

Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
