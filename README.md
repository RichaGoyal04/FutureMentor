# FutureMentor 🎓
## AI Job Mentor for Informal Workers
### Powered by IBM watsonx.ai Granite Models

> **Helping daily wage workers, artisans, gig workers, and rural job seekers discover better livelihood opportunities through personalised AI guidance — in their own language.**

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🤖 **AI Mentor** | Multilingual chat + voice input. Ask anything about jobs, skills, or schemes |
| 💼 **Jobs Dashboard** | AI-matched local jobs, gig work, government jobs, and self-employment with Opportunity Scores |
| 📚 **Skills Dashboard** | Skill gap analysis, free courses (PMKVY, Google, Skill India), resume check |
| 🏛️ **Govt Schemes** | Verified central & state schemes — eligibility, documents, apply steps |
| 🗺️ **Career Roadmap** | 30-day / 3-month / 6-month / 1-year personalised plans with income projections |

**Innovative extras:** AI Opportunity Score • Explainable recommendations • Voice input • Save offline • Daily career tips • Resume analyser • Dark mode • Glassmorphism UI

---

## 🏗️ Project Structure

```
FutureMentor/
├── run.py                    ← Start the app
├── requirements.txt
├── .env                      ← Your credentials (never commit!)
├── README.md
└── app/
    ├── __init__.py           ← Flask app factory
    ├── config.py             ← All config from .env
    ├── watsonx_client.py     ← IBM Granite API client (IAM token cache)
    ├── agent_instructions.py ← ⭐ ONLY file you edit to customise AI
    ├── blueprints/
    │   ├── main.py           ← Home + profile API + daily tip
    │   ├── mentor.py         ← /mentor — chat API
    │   ├── jobs.py           ← /jobs — recommendations
    │   ├── skills.py         ← /skills — gap analysis + resume
    │   ├── schemes.py        ← /schemes — govt scheme recommendations
    │   └── career.py         ← /career — roadmap generator
    ├── utils/
    │   └── prompt_builder.py ← All 6 AI prompt templates
    ├── templates/
    │   ├── base.html         ← Navbar, modals, Bootstrap 5
    │   ├── index.html        ← Home / landing page
    │   ├── mentor.html       ← Chat + voice UI
    │   ├── jobs.html         ← Jobs dashboard
    │   ├── skills.html       ← Skills dashboard
    │   ├── schemes.html      ← Government schemes
    │   └── career.html       ← Career roadmap
    └── static/
        ├── css/style.css     ← Dark mode, glassmorphism, animations
        └── js/app.js         ← Theme, profile, chat, voice, save
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | GET/POST | Save/load user profile |
| `/api/daily-tip` | GET | Today's career tip |
| `/mentor/api/chat` | POST | `{message}` → `{reply}` |
| `/mentor/api/history` | GET | Chat history |
| `/jobs/api/recommendations` | GET/POST | Job recommendations |
| `/skills/api/analysis` | GET/POST | Skill gap analysis |
| `/skills/api/resume` | POST | `{resume_text}` → `{analysis}` |
| `/schemes/api/recommendations` | GET/POST | Govt scheme recommendations |
| `/career/api/roadmap` | GET/POST | `{horizon}` → `{roadmap}` |
| `/health` | GET | Health check |

---

## 📋 Requirements

- Python 3.9+
- IBM Cloud account (free tier available)
- Watson Machine Learning service (Lite plan — free)
- Internet connection for AI calls

---

## 🤝 Helplines for Users

| Service | Number |
|---------|--------|
| Labour Helpline | 14434 |
| National Career Service | 1800-11-0001 |
| Fraud / Vigilance | 1800-111-555 |

---

*FutureMentor — AI Career Guide for India's Informal Workers*
*Powered by IBM watsonx.ai Granite Models*
