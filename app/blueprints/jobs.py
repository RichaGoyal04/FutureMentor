"""app/blueprints/jobs.py"""
import logging
from flask import Blueprint, jsonify, render_template, request, session
from app.utils.prompt_builder import jobs
from app.watsonx_client import generate_text

log = logging.getLogger(__name__)
jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("/")
def page():
    return render_template("jobs.html")


@jobs_bp.post("/api/recommendations")
def recommend():
    d = request.get_json(silent=True) or {}
    profile = {**session.get("profile", {}), **d}
    s, u = jobs(profile, filters=d)
    return jsonify({"recommendations": generate_text(u, s)})


@jobs_bp.get("/api/recommendations")
def recommend_get():
    s, u = jobs(session.get("profile", {}), filters={})
    return jsonify({"recommendations": generate_text(u, s)})
