#!/usr/bin/env python3
"""
Query the Family Office agent from the command line (no browser).

Usage:
  One-shot:   python scripts/query_agent.py "What tax strategies for California?"
  Interactive: python scripts/query_agent.py

  Persistence: Session is saved so the next run continues the same conversation.
  Start fresh: python scripts/query_agent.py --new   (or -n)
  Standardized test (no profile): python scripts/query_agent.py --test "Question?"   (uses POST /test)

  To match the question's state: AGENT_STATE=CA python scripts/query_agent.py "..."

Requires the backend to be running: cd backend && uvicorn app.main:app --reload
"""
import argparse
import json
import os
import sys
import uuid
import requests

BASE_URL = os.environ.get("AGENT_URL", "http://localhost:8000")

# Persist session across runs so follow-up questions keep context (same session on backend)
SESSION_FILE = os.path.join(os.path.dirname(__file__), ".agent_session")

# Override profile from env so the answer matches your question (e.g. state).
# Example: AGENT_STATE=CA python scripts/query_agent.py "What tax strategies in California?"
AGENT_STATE = os.environ.get("AGENT_STATE")
AGENT_INCOME = os.environ.get("AGENT_INCOME")  # e.g. 500000

DEFAULT_PROFILE = {
    "age": 45,
    "income": 500000,
    "filing_status": "married",
    "state": "NY",
    "assets": {"cash": 200000, "stocks": 1000000, "bonds": 300000, "real_estate": 500000},
    "family": {"marital_status": "married", "children": 2},
    "life_events": [],
    "goals": ["retirement planning", "tax efficiency"],
    "investment_goals": ["growth", "tax efficiency"],
    "estate_goals": ["estate tax minimization"],
    "risk_tolerance": "moderate",
    "time_horizon": "long-term",
}


def get_profile():
    """Build profile, applying AGENT_STATE / AGENT_INCOME env overrides."""
    p = dict(DEFAULT_PROFILE)
    if AGENT_STATE:
        p["state"] = AGENT_STATE.strip().upper()[:2]
    if AGENT_INCOME:
        try:
            p["income"] = float(AGENT_INCOME)
        except ValueError:
            pass
    return p


def load_session() -> str | None:
    """Return saved session_id if file exists and is valid, else None."""
    if not os.path.isfile(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sid = data.get("session_id")
        return sid if isinstance(sid, str) and sid else None
    except (json.JSONDecodeError, OSError):
        return None


def save_session(session_id: str) -> None:
    """Persist session_id so the next run can continue the same conversation."""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"session_id": session_id}, f)
    except OSError:
        pass


def clear_session() -> None:
    """Remove saved session (e.g. for --new)."""
    try:
        if os.path.isfile(SESSION_FILE):
            os.remove(SESSION_FILE)
    except OSError:
        pass


def check_backend():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False


def ask(session_id: str, message: str, profile: dict | None = None) -> dict:
    payload = {
        "session_id": session_id,
        "message": message,
    }
    if profile is not None:
        payload["user_profile"] = profile
    r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


def ask_test(message: str) -> dict:
    """Send question to standardized test endpoint (no profile)."""
    r = requests.post(f"{BASE_URL}/test", json={"message": message}, timeout=120)
    r.raise_for_status()
    return r.json()


def _is_session_not_found(exc: requests.HTTPError) -> bool:
    if exc.response.status_code != 400:
        return False
    try:
        detail = exc.response.json().get("detail", "")
        return "session" in detail.lower() and "not found" in detail.lower()
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Query Family Office agent from CLI.")
    parser.add_argument("-n", "--new", action="store_true", help="Start a new conversation (ignore saved session)")
    parser.add_argument("-t", "--test", action="store_true", help="Use /test endpoint (no profile, for standardized testing)")
    parser.add_argument("message", nargs="*", help="Question to ask (one-shot). Omit for interactive mode.")
    args = parser.parse_args()

    if not check_backend():
        print("Backend not running. Start it with:")
        print("  cd backend && uvicorn app.main:app --reload")
        sys.exit(1)

    # Standardized test mode: no profile, no session
    if args.test:
        if args.message:
            result = ask_test(" ".join(args.message))
            print(result["response"])
            if result.get("breakdown"):
                print("\n--- Breakdown ---")
                for k, v in result["breakdown"].items():
                    print(f"  {k}: {v}")
            if result.get("evidence"):
                print(f"\n--- Evidence ({len(result['evidence'])} docs) ---")
                for e in result["evidence"][:3]:
                    print(f"  [{e.get('doc_id', '?')}] {e.get('snippet', '')[:120]}...")
        else:
            print("Test mode (no profile). Type questions; empty line to quit.")
            while True:
                try:
                    line = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nBye.")
                    break
                if not line:
                    break
                try:
                    result = ask_test(line)
                    print("\nAgent:", result["response"])
                    if result.get("modules_used"):
                        print(f"  [modules: {', '.join(result['modules_used'])}]")
                    print()
                except Exception as e:
                    print(f"Error: {e}\n")
        return

    if args.new:
        clear_session()

    saved_id = load_session()
    if saved_id:
        session_id = saved_id
        profile = None  # backend already has profile for this session
    else:
        session_id = str(uuid.uuid4())
        profile = get_profile()

    message_parts = args.message
    one_shot = len(message_parts) > 0
    if one_shot:
        message = " ".join(message_parts)

    def do_ask(msg: str, send_profile: dict | None):
        try:
            return ask(session_id, msg, send_profile)
        except requests.HTTPError as e:
            if send_profile is None and _is_session_not_found(e):
                raise  # let caller recover
            raise

    if one_shot:
        try:
            result = do_ask(message, profile)
        except requests.HTTPError as e:
            if _is_session_not_found(e):
                clear_session()
                session_id = str(uuid.uuid4())
                profile = get_profile()
                result = ask(session_id, message, profile)
            else:
                raise
        save_session(session_id)
        print(result["response"])
        if result.get("breakdown"):
            print("\n--- Breakdown ---")
            for k, v in result["breakdown"].items():
                print(f"  {k}: {v}")
        if result.get("evidence"):
            print(f"\n--- Evidence ({len(result['evidence'])} docs) ---")
            for e in result["evidence"][:3]:
                print(f"  [{e.get('doc_id', '?')}] {e.get('snippet', '')[:120]}...")
        sys.exit(0)

    print("Family Office Agent (CLI). Type your question and press Enter. Empty line to quit.")
    print(f"Session: {session_id} (persisted for follow-ups)\n")
    while True:
        try:
            line = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not line:
            break
        try:
            result = do_ask(line, profile)
            profile = None
            save_session(session_id)
            print("\nAgent:", result["response"])
            if result.get("modules_used"):
                print(f"  [modules: {', '.join(result['modules_used'])}]")
            print()
        except requests.HTTPError as e:
            if _is_session_not_found(e):
                clear_session()
                session_id = str(uuid.uuid4())
                profile = get_profile()
                try:
                    result = ask(session_id, line, profile)
                    profile = None
                    save_session(session_id)
                    print("\nAgent:", result["response"])
                    if result.get("modules_used"):
                        print(f"  [modules: {', '.join(result['modules_used'])}]")
                    print()
                except Exception as e2:
                    print(f"Error: {e2}\n")
            else:
                print(f"Error: {e.response.status_code} - {e.response.text[:200]}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
