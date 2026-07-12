/**
 * FutureMentor — app.js
 * Theme | Profile | Chat | Voice | Save/Offline | Section loaders
 */
"use strict";

/* ══════════════════════════════════════════════════════
   1. THEME TOGGLE
══════════════════════════════════════════════════════ */
const Theme = {
  KEY: "fm_theme",
  apply(t) {
    document.documentElement.setAttribute("data-theme", t);
    const btn = document.getElementById("themeToggle");
    if (btn) btn.textContent = t === "dark" ? "☀️" : "🌙";
    localStorage.setItem(this.KEY, t);
  },
  toggle() {
    const cur = document.documentElement.getAttribute("data-theme") || "light";
    this.apply(cur === "dark" ? "light" : "dark");
  },
  init() {
    const saved = localStorage.getItem(this.KEY) ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    this.apply(saved);
    const btn = document.getElementById("themeToggle");
    if (btn) btn.addEventListener("click", () => Theme.toggle());
  },
};

/* ══════════════════════════════════════════════════════
   2. PROFILE — persist across page loads via localStorage + server session
══════════════════════════════════════════════════════ */
const Profile = {
  KEY: "fm_profile",

  defaults() {
    return {
      name: "Friend", occupation: "Worker", location: "India",
      education_level: "10th Pass", experience_years: 0,
      current_skills: "General labour", career_goal: "Better income",
      preferred_language: "English", income_current: "",
    };
  },

  load() {
    try { return { ...this.defaults(), ...JSON.parse(localStorage.getItem(this.KEY) || "{}") }; }
    catch { return this.defaults(); }
  },

  save(data) {
    const p = { ...this.load(), ...data };
    localStorage.setItem(this.KEY, JSON.stringify(p));
    // sync to server session
    fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    }).catch(() => {});
    return p;
  },

  fillForm(formId) {
    const p = this.load();
    const form = document.getElementById(formId);
    if (!form) return;
    Object.entries(p).forEach(([k, v]) => {
      const el = form.querySelector(`[name="${k}"]`) || form.querySelector(`#${k}`);
      if (el) el.value = v ?? "";
    });
  },

  collectForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    const fd = new FormData(form);
    const obj = {};
    for (const [k, v] of fd.entries()) obj[k] = v;
    // also collect by id for inputs without name
    form.querySelectorAll("input,select,textarea").forEach(el => {
      if (el.id && !obj[el.id]) obj[el.id] = el.value;
    });
    return obj;
  },

  renderBadge() {
    const p = this.load();
    const el = document.getElementById("profileBadge");
    if (el) el.textContent = p.name || "Friend";
    const loc = document.getElementById("profileLocation");
    if (loc) loc.textContent = p.location || "India";
    const occ = document.getElementById("profileOcc");
    if (occ) occ.textContent = p.occupation || "Worker";
  },
};

/* ══════════════════════════════════════════════════════
   3. TOAST NOTIFICATION
══════════════════════════════════════════════════════ */
function showToast(msg, type = "info") {
  const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };
  const colors = { success: "#10b981", error: "#ef4444", warning: "#f59e0b", info: "#6366f1" };
  const id = "toast_" + Date.now();
  const html = `
    <div id="${id}" class="toast fm-toast show align-items-center" role="alert"
         style="border-left:4px solid ${colors[type] || colors.info}">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <span>${icons[type] || icons.info}</span>
          <span>${msg}</span>
        </div>
        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    document.body.appendChild(container);
  }
  container.insertAdjacentHTML("beforeend", html);
  const el = document.getElementById(id);
  setTimeout(() => el && el.remove(), 4500);
}

/* ══════════════════════════════════════════════════════
   4. MARKDOWN-LITE RENDERER (bold, bullets, numbered)
══════════════════════════════════════════════════════ */
function renderMd(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^#{1,3} (.+)$/gm, "<strong>$1</strong>")
    .replace(/^[-•]\s(.+)$/gm, "&nbsp;• $1")
    .replace(/✅ Your Next Step:(.+)/g,
      '<div class="mt-3 p-3 rounded-xl" style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);color:var(--success)"><strong>✅ Your Next Step:</strong>$1</div>')
    .replace(/Opportunity Score[:\s]+(\d+)\/100/gi,
      '<span class="opp-score">⚡ $1/100</span>')
    .replace(/\n/g, "<br>");
}

/* ══════════════════════════════════════════════════════
   5. AI RESULT DISPLAY HELPERS
══════════════════════════════════════════════════════ */
function showLoading(el) {
  if (!el) return;
  el.innerHTML = `
    <div class="d-flex flex-column gap-2 p-2">
      <div class="d-flex align-items-center gap-3 text-muted mb-1">
        <div class="typing-dots"><span></span><span></span><span></span></div>
        <span>AI is thinking…</span>
      </div>
      <div class="skeleton" style="height:14px;width:90%"></div>
      <div class="skeleton" style="height:14px;width:75%"></div>
      <div class="skeleton" style="height:14px;width:85%"></div>
      <div class="skeleton" style="height:14px;width:60%"></div>
    </div>`;
  el.classList.add("loading");
}

function showResult(el, text) {
  if (!el) return;
  el.classList.remove("loading");
  el.innerHTML = renderMd(text);
  el.classList.add("animate-fadein");
}

function showError(el, msg) {
  if (!el) return;
  el.classList.remove("loading");
  el.innerHTML = `<div class="text-danger">❌ ${renderMd(msg)}</div>`;
}

/* ══════════════════════════════════════════════════════
   6. POST HELPER
══════════════════════════════════════════════════════ */
async function aiPost(url, payload, resultEl) {
  if (resultEl) showLoading(resultEl);
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`);
    return data;
  } catch (e) {
    if (resultEl) showError(resultEl, e.message);
    throw e;
  }
}

/* ══════════════════════════════════════════════════════
   7. SAVE / OFFLINE  (localStorage)
══════════════════════════════════════════════════════ */
const Saved = {
  KEY: "fm_saved",

  all() {
    try { return JSON.parse(localStorage.getItem(this.KEY) || "[]"); } catch { return []; }
  },

  add(title, content, section) {
    const items = this.all();
    items.unshift({ id: Date.now(), title, content, section, ts: new Date().toLocaleString() });
    localStorage.setItem(this.KEY, JSON.stringify(items.slice(0, 30)));
    showToast("Saved to My Recommendations ✅", "success");
    this.renderPanel();
  },

  remove(id) {
    const items = this.all().filter(x => x.id !== id);
    localStorage.setItem(this.KEY, JSON.stringify(items));
    this.renderPanel();
  },

  renderPanel() {
    const el = document.getElementById("savedList");
    if (!el) return;
    const items = this.all();
    if (!items.length) {
      el.innerHTML = '<p class="text-muted text-center fs-xs py-3">No saved items yet.</p>';
      return;
    }
    el.innerHTML = items.map(it => `
      <div class="saved-item mb-2">
        <div>
          <div class="fw-600" style="font-size:0.85rem">${it.title}</div>
          <div class="fs-xs text-muted">${it.section} · ${it.ts}</div>
        </div>
        <button class="btn btn-sm btn-glass" onclick="Saved.view(${it.id})">View</button>
      </div>`).join("");
  },

  view(id) {
    const it = this.all().find(x => x.id === id);
    if (!it) return;
    const modal = document.getElementById("savedViewModal");
    if (!modal) return;
    document.getElementById("savedViewTitle").textContent = it.title;
    document.getElementById("savedViewBody").innerHTML = renderMd(it.content);
    new bootstrap.Modal(modal).show();
  },
};

/* ══════════════════════════════════════════════════════
   8. CHAT (Mentor page)
══════════════════════════════════════════════════════ */
const Chat = {
  win: null,
  input: null,
  sendBtn: null,
  busy: false,

  init() {
    this.win     = document.getElementById("chatWindow");
    this.input   = document.getElementById("chatInput");
    this.sendBtn = document.getElementById("chatSend");
    if (!this.win) return;

    this.sendBtn?.addEventListener("click", () => this.send());
    this.input?.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); this.send(); }
    });
    document.getElementById("clearChat")?.addEventListener("click", () => this.clear());

    // load history from session
    fetch("/mentor/api/history").then(r => r.json()).then(h => {
      h.forEach(m => this.addMsg(m.role === "user" ? "user" : "bot", m.content));
    }).catch(() => {});

    // show welcome if empty
    if (!this.win.children.length) this.welcome();
  },

  welcome() {
    const p = Profile.load();
    this.addMsg("bot",
      `👋 Hello ${p.name}! I'm FutureMentor, your personal AI career guide.\n\n` +
      `I can help you find jobs near ${p.location}, learn new skills, ` +
      `discover government schemes, and plan your career path.\n\n` +
      `What would you like to explore today?`);
  },

  addMsg(role, text) {
    if (!this.win) return;
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.innerHTML = renderMd(text);
    this.win.appendChild(div);
    this.win.scrollTop = this.win.scrollHeight;
  },

  addTyping() {
    const div = document.createElement("div");
    div.className = "chat-msg bot";
    div.id = "typing_indicator";
    div.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    this.win.appendChild(div);
    this.win.scrollTop = this.win.scrollHeight;
    return div;
  },

  removeTyping() {
    document.getElementById("typing_indicator")?.remove();
  },

  async send() {
    if (this.busy || !this.input) return;
    const msg = this.input.value.trim();
    if (!msg) return;
    this.input.value = "";
    this.busy = true;
    if (this.sendBtn) this.sendBtn.disabled = true;

    this.addMsg("user", msg);
    const t = this.addTyping();

    try {
      const data = await aiPost("/mentor/api/chat", { message: msg }, null);
      this.removeTyping();
      this.addMsg("bot", data.reply);
    } catch (e) {
      this.removeTyping();
      this.addMsg("error", `Error: ${e.message}`);
    } finally {
      this.busy = false;
      if (this.sendBtn) this.sendBtn.disabled = false;
      this.input.focus();
    }
  },

  clear() {
    fetch("/mentor/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clear_history: true }),
    });
    if (this.win) this.win.innerHTML = "";
    this.welcome();
    showToast("Chat cleared", "info");
  },

  saveChat() {
    const text = Array.from(this.win?.querySelectorAll(".chat-msg") || [])
      .map(m => `[${m.classList.contains("user") ? "You" : "AI"}]: ${m.textContent}`)
      .join("\n\n");
    Saved.add("Chat Session", text, "AI Mentor");
  },
};

/* ══════════════════════════════════════════════════════
   9. VOICE INPUT (Web Speech API)
══════════════════════════════════════════════════════ */
const Voice = {
  rec: null,
  listening: false,

  init() {
    const btn = document.getElementById("voiceBtn");
    if (!btn) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      btn.title = "Voice not supported in this browser";
      btn.style.opacity = "0.4";
      return;
    }
    this.rec = new SR();
    this.rec.continuous = false;
    this.rec.interimResults = false;
    this.rec.lang = this._lang();

    this.rec.onresult = e => {
      const transcript = e.results[0][0].transcript;
      const inp = document.getElementById("chatInput");
      if (inp) inp.value = transcript;
      showToast(`🎤 "${transcript}"`, "info");
    };
    this.rec.onerror = () => this._stop(btn);
    this.rec.onend   = () => this._stop(btn);

    btn.addEventListener("click", () => {
      if (this.listening) { this.rec.stop(); this._stop(btn); }
      else { this.rec.lang = this._lang(); this.rec.start(); this._start(btn); }
    });
  },

  _lang() {
    const langMap = {
      Hindi: "hi-IN", Tamil: "ta-IN", Telugu: "te-IN", Bengali: "bn-IN",
      Marathi: "mr-IN", Kannada: "kn-IN", Malayalam: "ml-IN",
      Gujarati: "gu-IN", Punjabi: "pa-IN", English: "en-IN",
    };
    const p = Profile.load();
    return langMap[p.preferred_language] || "en-IN";
  },

  _start(btn) { this.listening = true;  btn.classList.add("listening");    btn.textContent = "🔴"; },
  _stop(btn)  { this.listening = false; btn.classList.remove("listening"); btn.textContent = "🎤"; },
};

/* ══════════════════════════════════════════════════════
   10. PROFILE MODAL
══════════════════════════════════════════════════════ */
const ProfileModal = {
  init() {
    Profile.fillForm("profileForm");
    Profile.renderBadge();
    document.getElementById("saveProfile")?.addEventListener("click", () => {
      const data = Profile.collectForm("profileForm");
      Profile.save(data);
      Profile.renderBadge();
      bootstrap.Modal.getInstance(document.getElementById("profileModal"))?.hide();
      showToast("Profile saved! 🎉", "success");
      // reload page section if present
      const page = document.body.dataset.page;
      if (page && PageLoaders[page]) PageLoaders[page]();
    });
  },
};

/* ══════════════════════════════════════════════════════
   11. DAILY TIP
══════════════════════════════════════════════════════ */
async function loadDailyTip() {
  const el = document.getElementById("dailyTipText");
  if (!el) return;
  el.textContent = "Loading your personalised tip…";
  try {
    const r = await fetch("/api/daily-tip");
    const d = await r.json();
    el.innerHTML = renderMd(d.tip || "Keep learning every day! 💪");
  } catch {
    el.textContent = "Today's tip: Update your skills to unlock better opportunities!";
  }
}

/* ══════════════════════════════════════════════════════
   12. SCORE RING ANIMATE
══════════════════════════════════════════════════════ */
function animateScore(el, score) {
  if (!el) return;
  const pct = Math.min(100, Math.max(0, parseInt(score) || 0));
  el.style.setProperty("--pct", `${pct}%`);
  el.querySelector("span").textContent = pct;
}

function extractScore(text) {
  const m = text.match(/(\d{1,3})\/100/);
  return m ? parseInt(m[1]) : 72;
}

/* ══════════════════════════════════════════════════════
   13. PAGE-SPECIFIC LOADERS
══════════════════════════════════════════════════════ */
const PageLoaders = {

  /* ── JOBS ── */
  jobs() {
    const resultEl = document.getElementById("jobsResult");
    const form = document.getElementById("jobsFilterForm");

    async function load(payload) {
      showLoading(resultEl);
      try {
        const d = await aiPost("/jobs/api/recommendations", payload, resultEl);
        showResult(resultEl, d.recommendations);
        document.getElementById("saveJobsBtn")?.classList.remove("d-none");
      } catch { /* error shown in resultEl */ }
    }

    document.getElementById("getJobsBtn")?.addEventListener("click", () => {
      const filters = form ? Object.fromEntries(new FormData(form)) : {};
      load({ ...Profile.load(), ...filters });
    });

    document.getElementById("saveJobsBtn")?.addEventListener("click", () => {
      Saved.add("Job Recommendations", resultEl.textContent, "Jobs");
    });

    // auto-load on page open
    load(Profile.load());
  },

  /* ── SKILLS ── */
  skills() {
    const resultEl = document.getElementById("skillsResult");
    const resumeEl = document.getElementById("resumeResult");

    async function loadAnalysis() {
      showLoading(resultEl);
      try {
        const d = await aiPost("/skills/api/analysis", Profile.load(), resultEl);
        showResult(resultEl, d.analysis);
        const ring = document.getElementById("skillScoreRing");
        if (ring) animateScore(ring, extractScore(d.analysis));
        document.getElementById("saveSkillsBtn")?.classList.remove("d-none");
      } catch { /* shown */ }
    }

    document.getElementById("analyseSkillsBtn")?.addEventListener("click", loadAnalysis);
    document.getElementById("saveSkillsBtn")?.addEventListener("click", () => {
      Saved.add("Skills Analysis", resultEl.textContent, "Skills");
    });

    document.getElementById("checkResumeBtn")?.addEventListener("click", async () => {
      const text = document.getElementById("resumeText")?.value.trim();
      if (!text) { showToast("Please paste your work history first", "warning"); return; }
      showLoading(resumeEl);
      try {
        const d = await aiPost("/skills/api/resume", { resume_text: text }, resumeEl);
        showResult(resumeEl, d.analysis);
      } catch { /* shown */ }
    });

    loadAnalysis();
  },

  /* ── SCHEMES ── */
  schemes() {
    const resultEl = document.getElementById("schemesResult");

    async function load(category) {
      showLoading(resultEl);
      try {
        const d = await aiPost("/schemes/api/recommendations",
          { ...Profile.load(), category }, resultEl);
        showResult(resultEl, d.recommendations);
        document.getElementById("saveSchemesBtn")?.classList.remove("d-none");
      } catch { /* shown */ }
    }

    document.getElementById("getSchemesBtn")?.addEventListener("click", () => {
      const cat = document.getElementById("schemeCategory")?.value || "";
      load(cat);
    });

    document.getElementById("saveSchemesBtn")?.addEventListener("click", () => {
      Saved.add("Government Schemes", resultEl.textContent, "Schemes");
    });

    document.querySelectorAll(".scheme-filter-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".scheme-filter-btn").forEach(b => b.classList.remove("btn-gradient"));
        btn.classList.add("btn-gradient");
        load(btn.dataset.category || "");
      });
    });

    load("");
  },

  /* ── CAREER ── */
  career() {
    const resultEl = document.getElementById("careerResult");

    async function load(horizon) {
      showLoading(resultEl);
      document.querySelectorAll(".horizon-tabs .nav-link").forEach(t =>
        t.classList.toggle("active", t.dataset.horizon === horizon));
      try {
        const d = await aiPost("/career/api/roadmap",
          { ...Profile.load(), horizon }, resultEl);
        showResult(resultEl, d.roadmap);
        document.getElementById("saveCareerBtn")?.classList.remove("d-none");
      } catch { /* shown */ }
    }

    document.querySelectorAll(".horizon-tabs .nav-link").forEach(tab => {
      tab.addEventListener("click", e => {
        e.preventDefault();
        load(tab.dataset.horizon || "full");
      });
    });

    document.getElementById("genRoadmapBtn")?.addEventListener("click", () => {
      const h = document.getElementById("horizonSelect")?.value || "full";
      load(h);
    });

    document.getElementById("saveCareerBtn")?.addEventListener("click", () => {
      Saved.add("Career Roadmap", resultEl.textContent, "Career");
    });

    load("full");
  },

  /* ── INDEX ── */
  index() {
    loadDailyTip();
    Profile.renderBadge();
  },

  /* ── MENTOR ── */
  mentor() {
    Chat.init();
    Voice.init();
    document.getElementById("saveChatBtn")?.addEventListener("click", () => Chat.saveChat());
    Profile.renderBadge();
  },
};

/* ══════════════════════════════════════════════════════
   14. INIT
══════════════════════════════════════════════════════ */
document.addEventListener("DOMContentLoaded", () => {
  Theme.init();
  ProfileModal.init();
  Saved.renderPanel();

  // sync profile to server on load
  const p = Profile.load();
  fetch("/api/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p),
  }).catch(() => {});

  // run page-specific loader
  const page = document.body.dataset.page;
  if (page && PageLoaders[page]) PageLoaders[page]();

  // animate score rings on page load
  document.querySelectorAll(".score-ring[data-score]").forEach(el => {
    animateScore(el, el.dataset.score);
  });

  // intersection observer for fade-up animations
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("animate-fadeup");
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll(".observe-me").forEach(el => obs.observe(el));
});

/* ══════════════════════════════════════════════════════
   15. EXPOSE GLOBALS (for inline calls)
══════════════════════════════════════════════════════ */
window.Profile = Profile;
window.Saved   = Saved;
window.Chat    = Chat;
window.showToast = showToast;
