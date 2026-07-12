"""
wsgi.py — Gunicorn entry point for Render, Railway, and production servers.
Gunicorn command: gunicorn wsgi:app
"""
from app import create_app

app = create_app("production")
