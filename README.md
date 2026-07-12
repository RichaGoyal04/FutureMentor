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
├── diagnose.py               ← Debug credentials & connectivity
├── restore.py                ← Regenerate all files if deleted
├── requirements.txt
├── .env                      ← Your credentials (never commit!)
├── .env.example              ← Template
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

## 🚀 Quick Start

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Set up IBM watsonx.ai
1. **Create an IBM Cloud account** (free): https://cloud.ibm.com/registration
2. **Get your API Key**: https://cloud.ibm.com/iam/apikeys → Create → Copy
3. **Create a watsonx.ai project**: https://dataplatform.cloud.ibm.com/projects
   - Click **New Project** → **Create an empty project**
   - Go to **Manage → General** → Copy the **Project ID**
4. **Activate Watson Machine Learning**:
   - Go to https://cloud.ibm.com/resources
   - Find **Watson Machine Learning** → Click **Activate**
   - In your project → **Manage → Services & Integrations** → Associate WML

### Step 3 — Configure credentials
```bash
cp .env.example .env
```
Edit `.env`:
```env
IBM_API_KEY=your_actual_api_key_here
IBM_PROJECT_ID=your_actual_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
SECRET_KEY=change-this-to-a-random-string
```

> ⚠️ **Region matters:** `ibm/granite-3-8b-instruct` is only available in `us-south` and `eu-de`. Use `https://us-south.ml.cloud.ibm.com` for best availability.

### Step 4 — Diagnose (optional but recommended)
```bash
python diagnose.py
```
This checks: API key, IAM token, project ID, model availability, and does a live generation test.

### Step 5 — Run
```bash
python run.py
```
Open: **http://localhost:5000**

---

## ⚙️ Customising AI Behaviour

Edit **`app/agent_instructions.py`** — this is the ONLY file you need to change:

```python
AGENT = {
    "persona_name":    "FutureMentor",          # Change the AI's name
    "tone":            "friendly-supportive",    # or "formal" | "casual"
    "primary_language": "English",              # Default reply language
    "supported_languages": ["Hindi", "Tamil",…],
    "job_recommendation": {
        "max_results": 6,                       # How many jobs to show
        "include_gig": True,                    # Include gig work?
    },
    "schemes": {
        "always_consider": ["MUDRA Loan", …],   # Schemes to check every time
    },
    "system_prompt": "…",                       # The master AI instruction
}
```

No other file needs to change.

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

## 🌐 Deployment

### Local (development)
```bash
python run.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 "app:create_app('production')"
```

### IBM Code Engine / Cloud Foundry
```bash
# Set environment variables in IBM Cloud dashboard, then deploy
ibmcloud cf push futurementor -b python_buildpack
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

---

## 🔒 Security

- IBM API key stored in `.env` only — never hardcoded
- `.env` listed in `.gitignore`
- IAM token cached in memory (never exposed to frontend)
- Session data stored server-side
- All user input sanitised before sending to AI

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Project ID not found" | Run `python diagnose.py` to see your valid Project IDs |
| "WML service inactive" | Activate at https://cloud.ibm.com/resources |
| "Model not available" | Use `us-south` region or change `WATSONX_MODEL_ID` |
| "API key invalid" | Renew at https://cloud.ibm.com/iam/apikeys |
| Blank AI responses | Check `.env` is configured and app is restarted |

For full diagnosis: `python diagnose.py`

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
