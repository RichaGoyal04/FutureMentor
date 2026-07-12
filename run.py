"""
run.py — FutureMentor development server entry point
Usage:  python run.py
"""
import os
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Default to 5001 — Windows often reserves 5000 for system services
    port = int(os.getenv("PORT", 5001))
    print(f"\n{'='*60}")
    print("  🎓 FutureMentor — AI Career Guide for Informal Workers")
    print(f"{'='*60}")
    print(f"  ▶  http://localhost:{port}")
    print(f"  🔧  Mode : {os.getenv('FLASK_ENV','development')}")
    print(f"  🤖  Model: {os.getenv('WATSONX_MODEL_ID','ibm/granite-4-h-small')}")
    print(f"  🌐  URL  : {os.getenv('IBM_WATSONX_URL','https://us-south.ml.cloud.ibm.com')}")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
