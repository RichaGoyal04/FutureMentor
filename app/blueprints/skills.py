"""app/blueprints/skills.py"""
import logging
from flask import Blueprint, jsonify, render_template, request, session
from app.utils.prompt_builder import skills, resume_check
from app.watsonx_client import generate_text

log = logging.getLogger(__name__)
skills_bp = Blueprint("skills", __name__)


@skills_bp.get("/")
def page():
    return render_template("skills.html")


@skills_bp.post("/api/analysis")
def analysis():
    d = request.get_json(silent=True) or {}
    profile = {**session.get("profile", {}), **d}
    s, u = skills(profile)
    return jsonify({"analysis": generate_text(u, s)})


@skills_bp.get("/api/analysis")
def analysis_get():
    s, u = skills(session.get("profile", {}))
    return jsonify({"analysis": generate_text(u, s)})


@skills_bp.post("/api/resume")
def resume():
    d = request.get_json(silent=True) or {}
    text = (d.get("resume_text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    s, u = resume_check(session.get("profile", {}), text)
    return jsonify({"analysis": generate_text(u, s)})
