#!/usr/bin/env python3
"""
Compare RAG+Agent vs. Direct LLM answers on standardized multiple-choice questions.

Calls two endpoints in parallel for each question:
  - POST /test        → full RAG + multi-module agent pipeline
  - POST /test/direct → LLM only, no RAG, no agent

Usage:
  python scripts/compare_tests.py [questions.jsonl] [options]

Options:
  -o, --output JSON   Write full results to a JSON file
  -n, --limit N       Run only the first N questions
  -v, --verbose       Print Q + both answers for every question
"""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = os.environ.get("AGENT_URL", "http://localhost:8000")
AGENT_ENDPOINT = f"{BASE_URL}/test"
DIRECT_ENDPOINT = f"{BASE_URL}/test/direct"
DEFAULT_QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "data", "aicpa_questions.jsonl")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_questions(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: invalid JSON line {i}: {e}", file=sys.stderr)
                continue
            q = obj.get("question") or obj.get("text") or obj.get("message")
            if not q:
                print(f"Warning: line {i} has no 'question': skipped", file=sys.stderr)
                continue
            yield {
                "id": obj.get("id", f"q{i}"),
                "question": q,
                "expected": obj.get("expected") or obj.get("expected_answer"),
            }


def normalize(text: str) -> str:
    if not text:
        return "?"
    text = text.strip().upper()
    m = re.search(r"\b([A-D])\b", text)
    return m.group(1) if m else (text[:1] if text else "?")


def call_agent(question: str, timeout: int = 120):
    """POST /test and return (letter, raw_answer, modules_used, error)."""
    try:
        r = requests.post(AGENT_ENDPOINT, json={"message": question}, timeout=timeout)
        r.raise_for_status()
        d = r.json()
        letter = normalize(d.get("response", ""))
        return letter, d.get("raw_answer") or d.get("response", ""), d.get("modules_used", []), None
    except Exception as e:
        return "?", "", [], str(e)


def call_direct(question: str, timeout: int = 120):
    """POST /test/direct and return (letter, raw_answer, error)."""
    try:
        r = requests.post(DIRECT_ENDPOINT, json={"message": question}, timeout=timeout)
        r.raise_for_status()
        d = r.json()
        letter = normalize(d.get("response", ""))
        return letter, d.get("raw_answer", ""), None
    except Exception as e:
        return "?", "", str(e)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_comparison(questions_path: str, verbose: bool, output_path: str | None, limit: int | None):
    if not os.path.isfile(questions_path):
        print(f"Questions file not found: {questions_path}", file=sys.stderr)
        sys.exit(1)

    items = list(load_questions(questions_path))
    if limit is not None:
        items = items[:limit]
        print(f"Running first {len(items)} questions (--limit {limit})", file=sys.stderr)
    total = len(items)
    if total == 0:
        print("No questions to run.", file=sys.stderr)
        return []

    results = []

    for i, item in enumerate(items, 1):
        qid = item["id"]
        question = item["question"]
        expected = item["expected"]

        print(f"[{i}/{total}] {qid} ... ", end="", flush=True)

        # Fire both requests in parallel
        with ThreadPoolExecutor(max_workers=2) as ex:
            fut_agent = ex.submit(call_agent, question)
            fut_direct = ex.submit(call_direct, question)
            agent_letter, agent_raw, modules_used, agent_err = fut_agent.result()
            direct_letter, direct_raw, direct_err = fut_direct.result()

        agent_passed  = (agent_letter  == expected) if expected else None
        direct_passed = (direct_letter == expected) if expected else None

        tag_agent  = "PASS" if agent_passed  else ("FAIL" if agent_passed  is False else "N/A")
        tag_direct = "PASS" if direct_passed else ("FAIL" if direct_passed is False else "N/A")

        print(f"agent={agent_letter}({tag_agent})  direct={direct_letter}({tag_direct})")

        if verbose:
            print(f"  Q: {question[:200]}{'...' if len(question) > 200 else ''}")
            print(f"  Expected:  {expected}")
            print(f"  Agent raw: {agent_raw[:300]}")
            print(f"  Direct raw:{direct_raw[:300]}")
            if agent_err:
                print(f"  Agent error: {agent_err}")
            if direct_err:
                print(f"  Direct error: {direct_err}")
        print()

        results.append({
            "id": qid,
            "expected": expected,
            # Agent (RAG + multi-module)
            "agent_response": agent_letter,
            "agent_passed": agent_passed,
            "agent_full_answer": agent_raw[:2000],
            "agent_modules_used": modules_used,
            "agent_error": agent_err,
            # Direct (LLM only)
            "direct_response": direct_letter,
            "direct_passed": direct_passed,
            "direct_full_answer": direct_raw[:2000],
            "direct_error": direct_err,
        })

    # Summary
    with_expected = [r for r in results if r["expected"] is not None]
    if with_expected:
        agent_score  = sum(1 for r in with_expected if r["agent_passed"])
        direct_score = sum(1 for r in with_expected if r["direct_passed"])
        n = len(with_expected)
        print("=" * 50)
        print(f"Results over {n} questions with expected answers:")
        print(f"  RAG + Agent:  {agent_score}/{n}  ({agent_score/n*100:.1f}%)")
        print(f"  Direct LLM:   {direct_score}/{n}  ({direct_score/n*100:.1f}%)")
        both_pass  = sum(1 for r in with_expected if r["agent_passed"] and r["direct_passed"])
        agent_only = sum(1 for r in with_expected if r["agent_passed"] and not r["direct_passed"])
        direct_only= sum(1 for r in with_expected if not r["agent_passed"] and r["direct_passed"])
        neither    = sum(1 for r in with_expected if not r["agent_passed"] and not r["direct_passed"])
        print(f"\n  Both correct: {both_pass}  Agent-only: {agent_only}  Direct-only: {direct_only}  Neither: {neither}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results written to {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Compare RAG+Agent vs Direct LLM on MC questions")
    parser.add_argument(
        "questions_file",
        nargs="?",
        default=DEFAULT_QUESTIONS_FILE,
        help="JSONL file with questions (default: scripts/data/aicpa_questions.jsonl)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print full Q&A")
    parser.add_argument("-o", "--output", metavar="JSON", help="Write full results to JSON file")
    parser.add_argument("-n", "--limit", type=int, metavar="N", help="Run only the first N questions")
    args = parser.parse_args()
    run_comparison(args.questions_file, args.verbose, args.output, args.limit)


if __name__ == "__main__":
    main()
