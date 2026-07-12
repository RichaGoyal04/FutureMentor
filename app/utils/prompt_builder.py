"""app/utils/prompt_builder.py — All AI prompt templates in one place."""
from app.agent_instructions import AGENT, build_system_prompt


def mentor_chat(profile: dict, message: str, history: list) -> tuple[str, str]:
    sys_p = build_system_prompt(profile)
    hist = "".join(
        f"{'User' if t['role']=='user' else AGENT['persona_name']}: {t['content']}\n"
        for t in history[-6:]
    )
    return sys_p, (
        f"{hist}User: {message}\n\n"
        "Give a helpful, encouraging reply. Mention a job, skill, or scheme if relevant. "
        "End with: Your Next Step: ..."
    )


def jobs(profile: dict, filters: dict) -> tuple[str, str]:
    n = AGENT["job_recommendation"]["max_results"]
    ext = ""
    if filters.get("work_type"):  ext += f" Focus on {filters['work_type']} work."
    if filters.get("sector"):     ext += f" Prioritise {filters['sector']} sector."
    if filters.get("min_salary"): ext += f" Minimum income Rs.{filters['min_salary']}/month."
    return build_system_prompt(profile), (
        f"Generate {n} personalised job recommendations for this user.{ext}\n\n"
        "For EACH job provide:\n"
        "1. **Job Title** and sector\n"
        "2. **Why it suits this user** (2 sentences)\n"
        "3. **Required Skills** (bullet list)\n"
        "4. **Estimated Income** (Rs./month or Rs./day)\n"
        "5. **Opportunity Score**: X/100\n"
        "6. **How to Apply** (numbered steps)\n\n"
        "Mix: local jobs, gig work, government jobs, self-employment. "
        "Mark top 2 with a star. Use simple language.\n\n"
        "End with: Your Next Step: [one action the user can take today]"
    )


def skills(profile: dict) -> tuple[str, str]:
    platforms = ", ".join(AGENT["skill_recommendation"]["platforms"][:5])
    return build_system_prompt(profile), (
        "Perform a Skill Gap Analysis.\n\n"
        "**Section 1 - Current Strengths**\n"
        "List valuable existing skills with their market value.\n\n"
        "**Section 2 - Skill Gaps** (4-6 skills)\n"
        "For each: name, why it matters, urgency (High/Medium/Low).\n\n"
        "**Section 3 - Learning Roadmap**\n"
        f"For each gap: best free resource (prefer: {platforms}), "
        "duration, expected salary boost, certification available.\n\n"
        "**Section 4 - Opportunity Score** (0-100) with one-line explanation.\n\n"
        "End with: Your Next Step: [most impactful skill to start today]"
    )


def schemes(profile: dict, filters: dict) -> tuple[str, str]:
    sl = ", ".join(AGENT["schemes"]["always_consider"][:8])
    cat = f" Focus on {filters['category']} schemes." if filters.get("category") else ""
    return build_system_prompt(profile), (
        f"Recommend VERIFIED government schemes this user qualifies for.{cat}\n\n"
        f"Always consider if eligible: {sl}.\n"
        "NEVER invent scheme names. Only real, active schemes.\n\n"
        "For EACH scheme:\n"
        "1. **Name** (official)\n"
        "2. **Type** (Central/State)\n"
        "3. **What it offers** (2 lines, plain language)\n"
        "4. **Eligibility** (check user profile)\n"
        "5. **Required Documents** (bullets)\n"
        "6. **How to Apply** (steps + official portal URL)\n"
        "7. **Expected Benefit** (amount/loan/service)\n"
        "8. **Opportunity Score**: X/100\n\n"
        "Genuine schemes never charge unofficial fees.\n\n"
        "End with: Your Next Step: [most impactful scheme to apply for today]"
    )


def roadmap(profile: dict, horizon: str) -> tuple[str, str]:
    focus = {
        "30_days":  "ONLY the 30-Day plan with daily action items.",
        "3_months": "ONLY the 3-Month plan.",
        "6_months": "ONLY the 6-Month plan.",
        "1_year":   "ONLY the 1-Year plan.",
        "full":     "All four plans: 30-Day, 3-Month, 6-Month, and 1-Year.",
    }.get(horizon, "All four plans.")
    return build_system_prompt(profile), (
        f"Create a personalised Career Roadmap. Generate {focus}\n\n"
        "For EACH horizon:\n"
        "- **Goal** - what to achieve\n"
        "- **Key Actions** - numbered weekly tasks\n"
        "- **Skills to Acquire**\n"
        "- **Milestones** - how to know you are on track\n"
        "- **Estimated Income** at end of period (Rs./month)\n"
        "- **Schemes to Apply** during this phase\n\n"
        "**Daily Tip**: one practical action for today.\n"
        "**Income Table**: Current > 30d > 3m > 6m > 1y\n\n"
        "Simple language, numbered lists.\n\n"
        "End with: Your Next Step: [most important action for tomorrow]"
    )


def resume_check(profile: dict, text: str) -> tuple[str, str]:
    return build_system_prompt(profile), (
        f"Analyse this work history and suggest improvements.\n\n"
        f"--- RESUME ---\n{text[:2000]}\n---\n\n"
        "1. **Strengths** - what is good\n"
        "2. **Improvements** - specific changes with examples\n"
        "3. **Keywords to Add** - for the target job\n"
        "4. **Suggested Bio** - 5-line professional bio\n"
        "5. **Readiness Score**: X/100\n\n"
        "End with: Your Next Step: [top improvement to make today]"
    )


def daily_tip(profile: dict) -> tuple[str, str]:
    return build_system_prompt(profile), (
        "Give one practical, personalised career tip for today. "
        "Must be: specific to occupation and location, actionable within 24 hours, "
        "free to implement, encouraging. 3-4 sentences max. "
        "End with a motivating one-liner in their preferred language."
    )
