"""
diagnose.py — FutureMentor credential and connectivity checker
Usage: python diagnose.py

Checks:
  1. .env file exists and required variables are set
  2. IBM IAM token can be fetched (API key valid)
  3. watsonx.ai endpoint reachable
  4. Project ID exists (WML platform API)
  5. Model available in the configured region
  6. Lists all Project IDs in your account
"""
import os, json, sys
import requests
from dotenv import load_dotenv

load_dotenv()

W   = "\033[93m"   # yellow
G   = "\033[92m"   # green
R   = "\033[91m"   # red
B   = "\033[94m"   # blue
RST = "\033[0m"
OK  = f"{G}  ✅{RST}"
ER  = f"{R}  ❌{RST}"
WN  = f"{W}  ⚠️{RST}"
INF = f"{B}  ℹ️{RST}"

def sep(): print("─" * 60)

def banner():
    print(f"\n{'═'*60}")
    print("   🔍  FutureMentor — Diagnostics")
    print(f"{'═'*60}")

# ── 1. .env variables ─────────────────────────────────────────────
def check_env():
    sep(); print(f"{B}[1] Environment Variables{RST}")
    required = ["IBM_API_KEY", "IBM_PROJECT_ID", "IBM_WATSONX_URL", "WATSONX_MODEL_ID"]
    ok = True
    for k in required:
        v = os.getenv(k, "")
        if v and v not in ("your_ibm_api_key_here", "your_project_id_here"):
            print(f"{OK} {k} = {v[:20]}…" if len(v) > 20 else f"{OK} {k} = {v}")
        else:
            print(f"{ER} {k} — NOT SET")
            ok = False
    return ok

# ── 2. IAM token ──────────────────────────────────────────────────
def get_token(api_key):
    sep(); print(f"{B}[2] IBM IAM Token{RST}")
    try:
        r = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
            timeout=30,
        )
        r.raise_for_status()
        t = r.json()["access_token"]
        print(f"{OK} IAM token obtained (expires in {r.json().get('expires_in',3600)}s)")
        return t
    except requests.HTTPError as e:
        print(f"{ER} IAM error {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        print(f"{ER} IAM request failed: {e}")
    return None

# ── 3. watsonx endpoint ───────────────────────────────────────────
def check_endpoint(url, token):
    sep(); print(f"{B}[3] watsonx.ai Endpoint Reachable{RST}")
    try:
        r = requests.get(
            f"{url}/ml/v1/foundation_model_specs?version=2023-05-29&limit=1",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        if r.status_code == 200:
            print(f"{OK} {url} — reachable")
            return True
        else:
            print(f"{WN} {url} returned HTTP {r.status_code}")
    except Exception as e:
        print(f"{ER} Cannot reach {url}: {e}")
    return False

# ── 4. List projects ──────────────────────────────────────────────
def list_projects(token):
    sep(); print(f"{B}[4] Your watsonx.ai Projects{RST}")
    try:
        r = requests.get(
            "https://api.dataplatform.cloud.ibm.com/v2/projects?limit=10",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        if r.status_code == 200:
            projects = r.json().get("resources", [])
            if not projects:
                print(f"{WN}  No projects found.")
                print(f"{INF}  Create one at: https://dataplatform.cloud.ibm.com/projects")
            for p in projects:
                pid  = p.get("metadata", {}).get("guid", "?")
                name = p.get("entity", {}).get("name", "Unnamed")
                print(f"{OK} [{name}]  ID: {pid}")
            return projects
        else:
            print(f"{ER} Projects API HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"{ER} Projects list failed: {e}")
    return []

# ── 5. Validate project ID ────────────────────────────────────────
def check_project(url, token, project_id, projects):
    sep(); print(f"{B}[5] Project ID in .env{RST}")
    found = any(p.get("metadata", {}).get("guid") == project_id for p in projects)
    if found:
        print(f"{OK} Project ID '{project_id}' exists in your account")
    else:
        print(f"{ER} Project ID '{project_id}' NOT FOUND in your account!")
        valid = [p.get("metadata", {}).get("guid","?") for p in projects]
        if valid:
            print(f"{INF}  Valid IDs in your account: {valid}")
            print(f"{INF}  Update IBM_PROJECT_ID in .env to one of the above")
        else:
            print(f"{INF}  No projects exist. Create one first.")

# ── 6. Check model ────────────────────────────────────────────────
def check_model(url, token, model_id):
    sep(); print(f"{B}[6] Model '{model_id}' in this region{RST}")
    try:
        r = requests.get(
            f"{url}/ml/v1/foundation_model_specs?version=2023-05-29&limit=200",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if r.status_code == 200:
            ids = [m.get("model_id","") for m in r.json().get("resources",[])]
            if model_id in ids:
                print(f"{OK} Model '{model_id}' is available in this region")
            else:
                print(f"{ER} Model '{model_id}' NOT available here")
                granite = [m for m in ids if "granite" in m.lower()]
                if granite:
                    print(f"{INF}  Available Granite models in this region:")
                    for m in granite[:10]:
                        print(f"       • {m}")
                    print(f"{INF}  → Update WATSONX_MODEL_ID in .env to one of the above")
        else:
            print(f"{WN} Could not list models: HTTP {r.status_code}")
    except Exception as e:
        print(f"{ER} Model check failed: {e}")

# ── 7. Test generation ────────────────────────────────────────────
def test_generation(url, token, model_id, project_id):
    sep(); print(f"{B}[7] Test Generation (short prompt){RST}")
    try:
        r = requests.post(
            f"{url}/ml/v1/text/generation?version=2023-05-29",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model_id":   model_id,
                "input":      "<|user|>\nSay hello in one sentence.\n<|assistant|>",
                "parameters": {"max_new_tokens": 50, "decoding_method": "greedy"},
                "project_id": project_id,
            },
            timeout=60,
        )
        if r.status_code == 200:
            text = r.json()["results"][0]["generated_text"].strip()
            print(f"{OK} Generation works!  Response: \"{text[:80]}\"")
        else:
            try:
                err = r.json().get("errors",[{}])[0]
                code = err.get("code","")
                msg  = err.get("message", r.text[:200])
            except Exception:
                code, msg = "", r.text[:200]
            print(f"{ER} HTTP {r.status_code} [{code}]: {msg[:250]}")
            if "inactive" in msg.lower() or code == "invalid_instance_status_error":
                print(f"{INF}  → Activate WML at https://cloud.ibm.com/resources")
                print(f"{INF}  → Then associate WML with your project")
    except Exception as e:
        print(f"{ER} Generation failed: {e}")

# ── Main ──────────────────────────────────────────────────────────
def main():
    banner()
    env_ok = check_env()
    if not env_ok:
        sep()
        print(f"{ER} Fix .env before continuing. Copy .env.example → .env and fill values.")
        print(f"{INF}  API Keys : https://cloud.ibm.com/iam/apikeys")
        print(f"{INF}  Projects : https://dataplatform.cloud.ibm.com/projects")
        sys.exit(1)

    api_key    = os.getenv("IBM_API_KEY")
    project_id = os.getenv("IBM_PROJECT_ID")
    url        = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model_id   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

    token = get_token(api_key)
    if not token:
        sep()
        print(f"{ER} Cannot proceed without a valid IAM token.")
        print(f"{INF}  Renew your API key at: https://cloud.ibm.com/iam/apikeys")
        sys.exit(1)

    reachable = check_endpoint(url, token)
    projects  = list_projects(token)
    if project_id:
        check_project(url, token, project_id, projects)

    if reachable:
        check_model(url, token, model_id)
        if project_id and projects:
            test_generation(url, token, model_id, project_id)

    sep()
    print(f"\n{G}  Diagnostics complete.{RST}")
    print(f"  If everything above shows ✅, run:  python run.py\n")

if __name__ == "__main__":
    main()
