"""app/blueprints/main.py"""
import logging
from flask import Blueprint, jsonify, render_template, request, session
from app.utils.prompt_builder import daily_tip
from app.watsonx_client import generate_text

log = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.post("/api/profile")
def save_profile():
    d = request.get_json(silent=True) or {}
    session["profile"] = {
        "user_name":          d.get("name", "friend"),
        "user_occupation":    d.get("occupation", "worker"),
        "user_location":      d.get("location", "India"),
        "education_level":    d.get("education_level", "basic"),
        "experience_years":   str(d.get("experience_years", "0")),
        "current_skills":     d.get("current_skills", ""),
        "career_goal":        d.get("career_goal", "improve livelihood"),
        "preferred_language": d.get("preferred_language", "English"),
        "income_current":     d.get("income_current", ""),
    }
    log.info("Profile saved: %s", session["profile"]["user_name"])
    return jsonify({"status": "ok", "profile": session["profile"]})


@main_bp.get("/api/profile")
def get_profile():
    return jsonify(session.get("profile", {}))


@main_bp.get("/api/daily-tip")
def get_daily_tip():
    p = session.get("profile", {})
    s, u = daily_tip(p)
    return jsonify({"tip": generate_text(u, s)})
