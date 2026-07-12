"""app/blueprints/career.py"""
import logging
from flask import Blueprint, jsonify, render_template, request, session
from app.utils.prompt_builder import roadmap
from app.watsonx_client import generate_text

log = logging.getLogger(__name__)
career_bp = Blueprint("career", __name__)


@career_bp.get("/")
def page():
    return render_template("career.html")


@career_bp.post("/api/roadmap")
def gen_roadmap():
    d = request.get_json(silent=True) or {}
    horizon = d.get("horizon", "full")
    profile = {**session.get("profile", {}), **d}
    s, u = roadmap(profile, horizon)
    return jsonify({"roadmap": generate_text(u, s), "horizon": horizon})


@career_bp.get("/api/roadmap")
def gen_roadmap_get():
    horizon = request.args.get("horizon", "full")
    s, u = roadmap(session.get("profile", {}), horizon)
    return jsonify({"roadmap": generate_text(u, s), "horizon": horizon})
