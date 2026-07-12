"""app/blueprints/schemes.py"""
import logging
from flask import Blueprint, jsonify, render_template, request, session
from app.utils.prompt_builder import schemes
from app.watsonx_client import generate_text

log = logging.getLogger(__name__)
schemes_bp = Blueprint("schemes", __name__)


@schemes_bp.get("/")
def page():
    return render_template("schemes.html")


@schemes_bp.post("/api/recommendations")
def recommend():
    d = request.get_json(silent=True) or {}
    profile = {**session.get("profile", {}), **d}
    s, u = schemes(profile, filters=d)
    return jsonify({"recommendations": generate_text(u, s)})


@schemes_bp.get("/api/recommendations")
def recommend_get():
    s, u = schemes(session.get("profile", {}), filters={})
    return jsonify({"recommendations": generate_text(u, s)})
