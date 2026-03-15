#!/usr/bin/env python3
"""
Run scenario-based open-ended tests against the agent and verify quality.

Each scenario provides a user profile + open-ended planning question along with:
  - expected_concepts : keywords/phrases that SHOULD appear in a good answer
  - grading_criteria  : free-text rubric fed to an LLM judge for a 1–10 score

Two grading methods are used for every scenario:
  1. Keyword Coverage  – fraction of expected_concepts found in the response
  2. LLM Judge Score   – Gemini/GPT rates the response 1-10 using the rubric

Usage:
  python scripts/run_scenario_tests.py [scenarios.jsonl] [options]

Options:
  -o, --output JSON   Write full results to a JSON file
  -n, --limit N       Run only the first N scenarios
  -v, --verbose       Print full agent response for every scenario
  --no-llm-judge      Skip the LLM judge step (faster, keyword-only)
"""
import argparse
import json
import os
import sys
import time
from typing import Optional

import requests

BASE_URL = os.environ.get("AGENT_URL", "http://localhost:8000")
SCENARIO_ENDPOINT = f"{BASE_URL}/test/scenario"
JUDGE_ENDPOINT = f"{BASE_URL}/judge"
DEFAULT_SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "data", "scenario_questions.jsonl")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_scenarios(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: invalid JSON on line {i}: {e}", file=sys.stderr)
                continue
            required = {"id", "profile", "question", "expected_concepts", "grading_criteria"}
            missing = required - obj.keys()
            if missing:
                print(f"Warning: scenario on line {i} missing fields {missing}: skipped", file=sys.stderr)
                continue
            yield obj


def keyword_coverage(response: str, concepts: list[str]) -> tuple[float, list[str], list[str]]:
    """Return (fraction, found_list, missing_list)."""
    text = response.lower()
    found, missing = [], []
    for concept in concepts:
        if concept.lower() in text:
            found.append(concept)
        else:
            missing.append(concept)
    fraction = len(found) / len(concepts) if concepts else 0.0
    return fraction, found, missing


def llm_judge_score(response: str, rubric: str) -> tuple[Optional[int], Optional[str]]:
    """
    Call POST /judge on the backend to score the response against the rubric.
    Returns (score, justification) or (None, error_message).
    """
    try:
        r = requests.post(
            JUDGE_ENDPOINT,
            json={"response": response, "rubric": rubric},
            timeout=60,
        )
        r.raise_for_status()
        d = r.json()
        return d.get("score"), d.get("justification")
    except Exception as e:
        return None, f"LLM judge error: {e}"


def call_scenario_endpoint(scenario: dict, timeout: int = 180) -> tuple[str, list, list, Optional[str]]:
    """POST /test/scenario. Returns (response_text, modules_used, evidence, error)."""
    payload = {
        "profile": scenario["profile"],
        "question": scenario["question"],
    }
    try:
        r = requests.post(SCENARIO_ENDPOINT, json=payload, timeout=timeout)
        r.raise_for_status()
        d = r.json()
        return d.get("response", ""), d.get("modules_used", []), d.get("evidence", []), None
    except requests.RequestException as e:
        detail = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                body = e.response.json()
                detail = body.get("detail", detail)
            except Exception:
                pass
        return "", [], [], detail


def bar(fraction: float, width: int = 20) -> str:
    filled = round(fraction * width)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {fraction*100:.0f}%"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_scenarios(
    scenarios_path: str,
    verbose: bool,
    output_path: Optional[str],
    limit: Optional[int],
    use_llm_judge: bool,
):
    if not os.path.isfile(scenarios_path):
        print(f"Scenarios file not found: {scenarios_path}", file=sys.stderr)
        sys.exit(1)

    scenarios = list(load_scenarios(scenarios_path))
    if limit is not None:
        scenarios = scenarios[:limit]
        print(f"Running first {len(scenarios)} scenarios (--limit {limit})\n", file=sys.stderr)
    total = len(scenarios)
    if total == 0:
        print("No scenarios to run.", file=sys.stderr)
        return []

    results = []
    total_keyword_score = 0.0
    total_llm_score = 0
    llm_score_count = 0

    for i, scenario in enumerate(scenarios, 1):
        sid = scenario["id"]
        name = scenario.get("name", sid)
        concepts = scenario["expected_concepts"]
        rubric = scenario["grading_criteria"]

        print(f"─" * 60)
        print(f"[{i}/{total}] {sid}: {name}")
        print(f"  Set: {scenario.get('set', 'N/A')}")
        print(f"  Calling /test/scenario ...", end=" ", flush=True)

        t0 = time.time()
        response_text, modules_used, evidence, error = call_scenario_endpoint(scenario)
        elapsed = time.time() - t0

        if error:
            print(f"ERROR ({elapsed:.1f}s)")
            print(f"  Error: {error}")
            results.append({
                "id": sid, "name": name, "ok": False,
                "error": error,
                "keyword_coverage": None, "keyword_score": None,
                "found_concepts": [], "missing_concepts": [],
                "llm_judge_score": None, "llm_judge_justification": None,
                "modules_used": [], "response": "",
            })
            print()
            continue

        print(f"done ({elapsed:.1f}s)")

        # --- Keyword coverage ---
        coverage, found, missing = keyword_coverage(response_text, concepts)
        total_keyword_score += coverage
        print(f"  Keyword coverage: {bar(coverage)}")
        if missing:
            print(f"  Missing concepts: {', '.join(missing)}")

        # --- LLM judge ---
        judge_score, judge_just = None, None
        if use_llm_judge:
            print(f"  Running LLM judge ...", end=" ", flush=True)
            judge_score, judge_just = llm_judge_score(response_text, rubric)
            if judge_score is not None:
                total_llm_score += judge_score
                llm_score_count += 1
                grade = "⬛" * (judge_score // 2) + f"  {judge_score}/10"
                print(f"{grade}")
                print(f"  Justification: {judge_just}")
            else:
                print(f"failed – {judge_just}")

        if verbose:
            print(f"\n  --- QUESTION ---\n  {scenario['question'][:300]}")
            print(f"\n  --- AGENT RESPONSE (first 600 chars) ---")
            for line in response_text[:600].splitlines():
                print(f"  {line}")
            if len(response_text) > 600:
                print("  ...")

        print(f"  Modules used: {modules_used}")
        print()

        results.append({
            "id": sid,
            "name": name,
            "set": scenario.get("set"),
            "ok": True,
            "keyword_coverage": round(coverage, 3),
            "keyword_score": f"{len(found)}/{len(concepts)}",
            "found_concepts": found,
            "missing_concepts": missing,
            "llm_judge_score": judge_score,
            "llm_judge_justification": judge_just,
            "modules_used": modules_used,
            "response": response_text,
            "grading_criteria": rubric,
            "expected_concepts": concepts,
        })

    # Summary
    ok_results = [r for r in results if r["ok"]]
    n = len(ok_results)
    print("=" * 60)
    print(f"SUMMARY  ({n}/{total} scenarios completed)")
    if n:
        avg_kw = total_keyword_score / n
        print(f"  Avg keyword coverage: {bar(avg_kw)}")
        if use_llm_judge and llm_score_count:
            avg_llm = total_llm_score / llm_score_count
            print(f"  Avg LLM judge score:  {avg_llm:.1f}/10  (n={llm_score_count})")

        # Per-set breakdown
        sets = {}
        for r in ok_results:
            s = r.get("set", "other")
            sets.setdefault(s, []).append(r.get("keyword_coverage", 0))
        if len(sets) > 1:
            print("\n  Per-set keyword coverage:")
            for s, scores in sets.items():
                avg = sum(scores) / len(scores)
                print(f"    {s:<20} {bar(avg, 15)}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results written to {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run scenario-based open-ended tests against the agent"
    )
    parser.add_argument(
        "scenarios_file",
        nargs="?",
        default=DEFAULT_SCENARIOS_FILE,
        help="JSONL file with scenario definitions (default: scripts/data/scenario_questions.jsonl)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print full agent responses")
    parser.add_argument("-o", "--output", metavar="JSON", help="Write results to JSON file")
    parser.add_argument("-n", "--limit", type=int, metavar="N", help="Run only first N scenarios")
    parser.add_argument(
        "--no-llm-judge", dest="llm_judge", action="store_false",
        help="Skip the LLM judge scoring step (faster)"
    )
    parser.set_defaults(llm_judge=True)
    args = parser.parse_args()
    run_scenarios(args.scenarios_file, args.verbose, args.output, args.limit, args.llm_judge)


if __name__ == "__main__":
    main()
