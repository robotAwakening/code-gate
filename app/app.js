/* ============================================================
   code-gate — app logic (vanilla JS, no dependencies)
   ============================================================ */

const API = "";               // same origin
let currentChallenge = null;  // challenge object from /api/challenge
let selectedOption   = null;  // currently highlighted option text

// ── Helpers ──────────────────────────────────────────────────
function show(id)  { document.getElementById(id).hidden = false; }
function hide(id)  { document.getElementById(id).hidden = true;  }
function el(id)    { return document.getElementById(id); }
function text(id, t) { el(id).textContent = t; }

function showScreen(name) {
  for (const s of document.querySelectorAll(".screen")) s.hidden = true;
  show("screen" + name);
}

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Status badge update ───────────────────────────────────────
function updateBadges(state) {
  if (state.total_challenges_solved > 0 || state.daily_streak > 0) {
    show("statsRow");
    text("streakCount", state.daily_streak);
    text("totalCount",  state.total_challenges_solved);
  } else {
    hide("statsRow");
  }
}

// ── Difficulty helpers ────────────────────────────────────────
const DIFF_LABELS = { 1: "Easy", 2: "Medium", 3: "Hard" };
const DIFF_CLASS  = { 1: "easy", 2: "medium", 3: "hard" };

function renderDifficultyPill(diffLevel, targetEl) {
  targetEl.textContent = DIFF_LABELS[diffLevel] || "Easy";
  targetEl.className   = "difficulty-pill " + (DIFF_CLASS[diffLevel] || "easy");
}

function renderDifficultyDots(diffLevel) {
  const dotsEl = el("difficultyDots");
  dotsEl.innerHTML = "";
  for (let i = 1; i <= 3; i++) {
    const d = document.createElement("span");
    d.className = "dot" + (i <= diffLevel ? " active" : "");
    dotsEl.appendChild(d);
  }
}

// ── Gate screen ───────────────────────────────────────────────
async function loadGateScreen() {
  showScreen("Loading");
  try {
    const [status, challenge] = await Promise.all([
      apiFetch("/api/status"),
      apiFetch("/api/challenge"),
    ]);

    updateBadges(status);

    if (status.is_unlocked) {
      renderUnlockedScreen(status);
      return;
    }

    // Show gate
    const attempts = status.unlock_attempts_today;
    renderDifficultyPill(challenge.difficulty, el("difficultyPill"));

    const attemptsHint = el("attemptsHint");
    if (attempts === 0) {
      attemptsHint.textContent = "No attempts yet today.";
    } else {
      attemptsHint.textContent =
        `${attempts} attempt${attempts !== 1 ? "s" : ""} today — difficulty increases with each try.`;
    }

    currentChallenge = challenge;
    showScreen("Gate");
  } catch (err) {
    showScreen("Loading");
    el("screenLoading").querySelector(".hint").textContent =
      "Could not reach the server. Make sure it is running.";
  }
}

// ── Challenge screen ──────────────────────────────────────────
function renderChallengeScreen(challenge) {
  currentChallenge = challenge;
  selectedOption   = null;

  // Category badge
  const catIcons = { math: "🔢 Math", coding: "💻 Coding", logic: "🧠 Logic" };
  text("categoryBadge", catIcons[challenge.category] || challenge.category);

  renderDifficultyDots(challenge.difficulty);

  text("challengeQuestion", challenge.question);

  if (challenge.options && challenge.options.length > 0) {
    buildOptionsGrid(challenge.options);
    show("optionsGrid");
    hide("answerGroup");
  } else {
    hide("optionsGrid");
    el("answerInput").value = "";
    show("answerGroup");
    setTimeout(() => el("answerInput").focus(), 100);
  }

  showScreen("Challenge");
}

function buildOptionsGrid(options) {
  const grid = el("optionsGrid");
  grid.innerHTML = "";
  for (const opt of options) {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.textContent = opt;
    btn.addEventListener("click", () => selectOption(btn, opt));
    grid.appendChild(btn);
  }
}

function selectOption(btn, value) {
  // Deselect all
  for (const b of el("optionsGrid").querySelectorAll(".option-btn")) {
    b.classList.remove("selected");
  }
  btn.classList.add("selected");
  selectedOption = value;
  // Auto-submit after a short delay for snappy UX
  setTimeout(() => submitAnswer(value), 350);
}

// ── Submit answer ─────────────────────────────────────────────
async function submitAnswer(overrideValue) {
  const answer = overrideValue !== undefined
    ? overrideValue
    : el("answerInput").value.trim();

  if (!answer) return;

  // Disable inputs during submission
  el("btnSubmitAnswer").disabled = true;
  for (const b of el("optionsGrid").querySelectorAll(".option-btn")) b.disabled = true;

  try {
    const result = await apiFetch("/api/solve", {
      method: "POST",
      body: JSON.stringify({ challenge_id: currentChallenge.id, answer }),
    });

    updateBadges(result);

    // Flash correct/wrong state on options
    if (currentChallenge.options) {
      for (const b of el("optionsGrid").querySelectorAll(".option-btn")) {
        if (b.textContent === currentChallenge.answer) b.classList.add("correct");
        if (b.classList.contains("selected") && !result.correct) b.classList.add("wrong");
      }
      // Brief pause so user sees feedback before moving on
      await new Promise(r => setTimeout(r, 700));
    }

    if (result.unlocked) {
      renderUnlockedScreen(result);
    } else {
      renderResultScreen(result, answer);
    }
  } catch (err) {
    el("btnSubmitAnswer").disabled = false;
    for (const b of el("optionsGrid").querySelectorAll(".option-btn")) b.disabled = false;
    alert("Network error — please try again.");
  }
}

// ── Result screen ─────────────────────────────────────────────
function renderResultScreen(result, userAnswer) {
  if (result.correct) {
    text("resultIcon",  "✅");
    text("resultTitle", "Correct!");
    text("resultBody",  "Well done! But you still need one correct answer to unlock.");
  } else {
    text("resultIcon",  "❌");
    text("resultTitle", "Not quite.");
    text("resultBody",  `The correct answer was: "${currentChallenge.answer}"`);
  }

  const attempts = result.unlock_attempts_today;
  const nextDiff = attempts <= 1 ? 1 : attempts <= 3 ? 2 : 3;
  renderDifficultyPill(nextDiff, document.createElement("span")); // just compute label

  const afterBtn = el("btnAfterResult");
  afterBtn.textContent = result.correct ? "Try Another" : "Try Again";
  afterBtn.onclick = () => fetchAndShowChallenge();

  const tryAnotherBtn = el("btnTryAnother");
  tryAnotherBtn.hidden = true;

  showScreen("Result");
}

async function fetchAndShowChallenge() {
  showScreen("Loading");
  try {
    const challenge = await apiFetch("/api/challenge");
    renderChallengeScreen(challenge);
  } catch {
    loadGateScreen();
  }
}

// ── Unlocked screen ───────────────────────────────────────────
function renderUnlockedScreen(state) {
  const streakEl = el("streakCelebrate");
  if (state.daily_streak >= 2) {
    el("streakCelebrateCount").textContent = state.daily_streak;
    streakEl.hidden = false;
  } else {
    streakEl.hidden = true;
  }
  showScreen("Unlocked");
}

// ── Event wiring ──────────────────────────────────────────────
el("btnStartChallenge").addEventListener("click", () => {
  if (currentChallenge) renderChallengeScreen(currentChallenge);
  else fetchAndShowChallenge();
});

el("btnSubmitAnswer").addEventListener("click", () => submitAnswer());

el("answerInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitAnswer();
});

el("btnBackToGate").addEventListener("click", loadGateScreen);

el("btnAfterResult").addEventListener("click", fetchAndShowChallenge);

el("btnPracticeMode").addEventListener("click", fetchAndShowChallenge);

el("btnReset").addEventListener("click", async () => {
  if (!confirm("Reset gate? This clears today's unlock status.")) return;
  try {
    await apiFetch("/api/reset", { method: "POST" });
    loadGateScreen();
  } catch {
    alert("Error resetting.");
  }
});

// ── PWA service-worker registration ──────────────────────────
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

// ── Boot ──────────────────────────────────────────────────────
loadGateScreen();
