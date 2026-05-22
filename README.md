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
- Allow "challenge-only mode" (practice without unlocking intent).

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
- Added a rich challenge engine in `code_gate/challenges.py` with 21 built-in challenges across three categories (Math, Coding, Logic) and three difficulty tiers (Easy → Medium → Hard). Difficulty automatically escalates with the number of unlock attempts made today.
- Added daily streak tracking to `GateState` (persisted in `~/.code_gate/state.json`).
- Added a PWA (Progressive Web App) frontend in `app/` — mobile-first dark-theme UI with multiple-choice tap targets, difficulty badges, and streak celebration.
- Added a built-in HTTP server in `code_gate/server.py` that serves the PWA and exposes a JSON API — no external dependencies required.

Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📱 Run on Your Phone (step-by-step)

The app is a **PWA (Progressive Web App)** served by a Python HTTP server.
Both your computer and phone must be on the **same Wi-Fi network**.

### Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9+ | Check: `python3 --version` |
| Git | To clone the repo |
| Any modern browser on phone | Chrome (Android/iOS) or Safari (iOS) |

No app-store install required. The browser-based PWA works on **both Android and iPhone**.

---

### Step 1 — Clone and enter the repo

```bash
git clone https://github.com/robotAwakening/code-gate.git
cd code-gate
```

### Step 2 — Start the server

```bash
python -m code_gate.server
```

You will see output like:

```
code-gate server running on port 5000
  Local:   http://localhost:5000
  Network: http://192.168.1.42:5000
Open either URL in your phone's browser (same Wi-Fi network required for Network URL).
Press Ctrl+C to stop.
```

> **Note the Network URL** — that is the address you will type into your phone.

To use a different port (e.g. if 5000 is taken):

```bash
python -m code_gate.server --port 8080
```

### Step 3 — Find your computer's local IP (if the server didn't print it)

**macOS / Linux:**
```bash
ipconfig getifaddr en0   # macOS Wi-Fi
# or
ip route get 8.8.8.8 | awk '{print $7; exit}'  # Linux
```

**Windows (Command Prompt):**
```
ipconfig
```
Look for `IPv4 Address` under your active Wi-Fi adapter (e.g. `192.168.1.42`).

### Step 4 — Open on your phone

1. Make sure your phone is connected to the **same Wi-Fi** as your computer.
2. Open **Chrome** (Android) or **Safari** (iOS).
3. Type the Network URL from Step 2 into the address bar, e.g.:
   ```
   http://192.168.1.42:5000
   ```
4. The Code Gate app will load. You should see the 🔒 gate screen.

### Step 5 — Add to Home Screen (optional, but recommended for the full app experience)

**Android (Chrome):**
1. Tap the three-dot menu (⋮) in Chrome.
2. Tap **Add to Home screen**.
3. Tap **Add**.

**iPhone (Safari):**
1. Tap the Share button (□↑) at the bottom.
2. Scroll down and tap **Add to Home Screen**.
3. Tap **Add**.

Once added, the app opens full-screen without browser chrome, just like a native app.

---

### API endpoints (for developers)

| Endpoint | Method | Description |
|---|---|---|
| `GET /api/status` | GET | Current gate state (locked/unlocked, streak, etc.) |
| `GET /api/challenge` | GET | Fetch a challenge at the current difficulty |
| `POST /api/solve` | POST | Submit an answer `{"challenge_id": N, "answer": "..."}` |
| `POST /api/reset` | POST | Reset today's state |
| `GET /` | GET | Serves the PWA shell |

---

### Troubleshooting

| Problem | Fix |
|---|---|
| Phone shows "This site can't be reached" | Check phone and computer are on the **same Wi-Fi** network. Confirm server is running. |
| `Address already in use` error | Use `--port 8080` (or another free port). |
| Page loads but API calls fail | Check your firewall allows inbound connections on port 5000. On macOS: System Settings → Firewall. On Windows: allow Python through Windows Defender Firewall. |
| iOS Safari shows blank screen | Hard-reload: hold the refresh button → tap "Reload Without Content Blockers". |
| Server prints `127.0.0.1` for Network URL | Your machine may have no active Wi-Fi. Connect to Wi-Fi and restart the server. |

---

## Run and execute locally (CLI prototype)

This repository also includes a command-line prototype for the blocking-gate logic.

From the repo root:

```bash
# show current gate status
python -m code_gate.cli status

# check if an app package is blocked
python -m code_gate.cli check-app com.google.android.youtube

# check if a URL/host is blocked
python -m code_gate.cli check-url https://www.instagram.com/reel/example

# solve one challenge (unlocks after one correct answer: 2 + 2 = 4)
python -m code_gate.cli solve

# reset local state
python -m code_gate.cli reset
```

State is persisted by default at `~/.code_gate/state.json`, so unlock progress survives restarts.
