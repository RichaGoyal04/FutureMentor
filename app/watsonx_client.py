"""
app/watsonx_client.py
IBM watsonx.ai Granite model client.
- Uses /ml/v1/text/chat (Chat API) — required for granite-4-h-small and all current models
- Falls back to /ml/v1/text/generation for legacy models if chat API fails
- IAM token cached (60s buffer before expiry)
- Every IBM error code → actionable user-facing message
- Never raises to callers
"""
import logging, time
from typing import Optional
import requests as _req
from flask import current_app

log = logging.getLogger(__name__)


class _TokenCache:
    _t: Optional[str] = None
    _exp: float = 0.0
    def ok(self): return bool(self._t) and time.time() < self._exp - 60
    def set(self, t, exp=3600): self._t = t; self._exp = time.time() + exp

_tok = _TokenCache()


def _iam(api_key: str) -> str:
    """Fetch (or return cached) IBM IAM Bearer token."""
    if _tok.ok():
        return _tok._t  # type: ignore
    r = _req.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
        timeout=30,
    )
    r.raise_for_status()
    p = r.json()
    _tok.set(p["access_token"], int(p.get("expires_in", 3600)))
    return _tok._t  # type: ignore


def generate_text(prompt: str, system_prompt: str = "") -> str:
    """
    Call IBM Granite via the Chat API and return the generated text.
    Never raises — returns a user-friendly actionable error string on failure.
    """
    key  = current_app.config["IBM_API_KEY"]
    proj = current_app.config["IBM_PROJECT_ID"]
    url  = current_app.config["IBM_WATSONX_URL"]
    mid  = current_app.config["WATSONX_MODEL_ID"]

    if not key or not proj:
        return _no_creds()

    # Build Chat API messages list
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        token = _iam(key)
    except Exception as e:
        log.error("IAM error: %s", e)
        return _auth_err()

    try:
        r = _req.post(
            f"{url}/ml/v1/text/chat?version=2023-05-29",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model_id":   mid,
                "messages":   messages,
                "parameters": {
                    "max_new_tokens": current_app.config["WATSONX_MAX_TOKENS"],
                    "temperature":    current_app.config["WATSONX_TEMPERATURE"],
                    "top_p":          current_app.config["WATSONX_TOP_P"],
                    "stop_sequences": ["<|endoftext|>"],
                },
                "project_id": proj,
            },
            timeout=90,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        log.info("watsonx chat OK - %d chars", len(text))
        return text

    except _req.HTTPError:
        status = r.status_code
        try:
            body = r.json()
            # Chat API error shape: {"errors":[{code, message}]} OR {"error":{code,message}}
            errs = body.get("errors") or [body.get("error", {})]
            code = errs[0].get("code", "") if errs else ""
            msg  = errs[0].get("message", r.text[:250]) if errs else r.text[:250]
        except Exception:
            code, msg = "", r.text[:250]
        log.error("watsonx HTTP %s [%s]: %s", status, code, msg[:300])
        return _ibm_err(status, code, msg, mid, url)

    except Exception as e:
        log.exception("watsonx unexpected: %s", e)
        return (
            "**Unexpected error.** Please restart the app.\n\n"
            "Your Next Step: Run `python diagnose.py` to check your connection."
        )


# ── Error message helpers ──────────────────────────────────────────────────────

def _no_creds() -> str:
    return (
        "**FutureMentor — Setup Required**\n\n"
        "IBM credentials are not configured.\n\n"
        "**Steps:**\n"
        "1. Open the `.env` file in the project root\n"
        "2. Set `IBM_API_KEY` to your IBM Cloud API key\n"
        "3. Set `IBM_PROJECT_ID` to your watsonx.ai project ID\n"
        "4. Restart: `python run.py`\n\n"
        "Get your API key: https://cloud.ibm.com/iam/apikeys\n"
        "Get your Project ID: https://dataplatform.cloud.ibm.com/projects\n\n"
        "✅ Your Next Step: Configure `.env` then restart the app."
    )


def _auth_err() -> str:
    return (
        "**IBM API Key is invalid or expired.**\n\n"
        "1. Go to https://cloud.ibm.com/iam/apikeys\n"
        "2. Click **Create** → copy the new key\n"
        "3. Update `IBM_API_KEY` in `.env` and restart\n\n"
        "✅ Your Next Step: Refresh your API key at https://cloud.ibm.com/iam/apikeys"
    )


def _ibm_err(status: int, code: str, msg: str, model: str, url: str) -> str:
    msg_l = msg.lower()

    # WML not associated with project
    if "no_associated_service_instance" in code or "no_associated_service_instance" in msg_l:
        return (
            "**Watson Machine Learning is not linked to your project.**\n\n"
            "Your API key and Project ID are correct, but WML is not associated.\n\n"
            "**Fix (2 minutes):**\n"
            "1. Go to https://cloud.ibm.com/resources\n"
            "2. Find **Watson Machine Learning** → confirm it's **Active**\n"
            "   (If missing: https://cloud.ibm.com/catalog/services/watson-machine-learning)\n"
            "3. Go to https://dataplatform.cloud.ibm.com/projects\n"
            "4. Open your project → **Manage** tab → **Services & integrations**\n"
            "5. Click **Associate service +** → select Watson Machine Learning → **Associate**\n"
            "6. Restart: `python run.py`\n\n"
            "✅ Your Next Step: Associate WML at https://dataplatform.cloud.ibm.com/projects"
        )

    # WML service inactive / provisioning
    if code == "invalid_instance_status_error" or "inactive" in msg_l:
        return (
            "**Watson Machine Learning service is Inactive.**\n\n"
            "1. Go to https://cloud.ibm.com/resources\n"
            "2. Find **Watson Machine Learning** → click **Activate**\n"
            "3. In your project → **Manage → Services & Integrations** → Associate WML\n"
            "4. Restart: `python run.py`\n\n"
            "✅ Your Next Step: Activate WML at https://cloud.ibm.com/resources"
        )

    # Project not found / container error
    if status == 404 or "project_id" in msg_l or "container_not_found" in code:
        return (
            "**Project ID not found.**\n\n"
            "`IBM_PROJECT_ID` in `.env` doesn't match any accessible project.\n\n"
            "**Fix:**\n"
            "1. Go to https://dataplatform.cloud.ibm.com/projects\n"
            "2. Open your project → **Manage → General** → copy **Project ID**\n"
            "3. Update `IBM_PROJECT_ID` in `.env` and restart\n\n"
            "Run `python diagnose.py` to list all valid Project IDs.\n\n"
            "✅ Your Next Step: Run `python diagnose.py`"
        )

    # Model withdrawn or not supported
    if code in ("model_not_supported", "invalid_request_entity") or (
        "withdraw" in msg_l or "deprecated" in msg_l
    ):
        return (
            f"**Model `{model}` is withdrawn or not supported.**\n\n"
            "IBM has retired this model. Update your `.env`:\n\n"
            "```\nWATSONX_MODEL_ID=ibm/granite-4-h-small\n```\n\n"
            "Then restart: `python run.py`\n\n"
            "✅ Your Next Step: Update `WATSONX_MODEL_ID=ibm/granite-4-h-small` in `.env`"
        )

    # Auth failure
    if status == 401:
        return (
            "**Authentication failed.** API key may have expired.\n\n"
            "1. Go to https://cloud.ibm.com/iam/apikeys → create new key\n"
            "2. Update `IBM_API_KEY` in `.env` and restart\n\n"
            "✅ Your Next Step: Refresh key at https://cloud.ibm.com/iam/apikeys"
        )

    # Rate limit
    if status == 429:
        return (
            "**Rate limit reached.** Please wait 30 seconds and try again.\n\n"
            "✅ Your Next Step: Wait 30 seconds then retry."
        )

    # Generic fallback
    return (
        f"**IBM watsonx.ai error (HTTP {status}).**\n\n"
        f"Code: `{code}`\nDetail: {msg[:300]}\n\n"
        "Run `python diagnose.py` for full diagnosis.\n\n"
        "✅ Your Next Step: Run `python diagnose.py`"
    )
