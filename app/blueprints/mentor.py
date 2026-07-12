"""app/blueprints/mentor.py"""
import logging
from flask import Blueprint, jsonify, render_template, request, session
from app.utils.prompt_builder import mentor_chat
from app.watsonx_client import generate_text

log = logging.getLogger(__name__)
mentor_bp = Blueprint("mentor", __name__)
_MAX = 20


@mentor_bp.get("/")
def page():
    return render_template("mentor.html")


@mentor_bp.post("/api/chat")
def chat():
    d = request.get_json(silent=True) or {}
    if d.get("clear_history"):
        session["chat_history"] = []
        return jsonify({"reply": "Chat cleared! How can I help you?", "history": []})
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Empty message"}), 400
    hist    = session.get("chat_history", [])
    profile = session.get("profile", {})
    s, u    = mentor_chat(profile, msg, hist)
    reply   = generate_text(u, s)
    hist.append({"role": "user",      "content": msg})
    hist.append({"role": "assistant", "content": reply})
    session["chat_history"] = hist[-_MAX:]
    return jsonify({"reply": reply, "history": session["chat_history"]})


@mentor_bp.get("/api/history")
def history():
    return jsonify(session.get("chat_history", []))
