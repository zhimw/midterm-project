#!/usr/bin/env python3
"""
Run standardized tests (e.g. AICPA-style multiple choice) against the agent.

Uses the /test API so no user profile is required. Reads questions from a JSONL file.

Usage:
  python scripts/run_standardized_tests.py [options] [questions.jsonl]

  If no file is given, reads from scripts/data/sample_questions.jsonl (create from sample below).

Question JSONL format (one JSON object per line):
  {"id": "q1", "question": "Full question text...", "expected": "A"}
  {"question": "Question without id or expected answer"}

Output: prints each response and optional pass/fail if "expected" is provided.
"""
import argparse
import json
import os
import re
import sys

import requests

BASE_URL = os.environ.get("AGENT_URL", "http://localhost:8000")
TEST_ENDPOINT = f"{BASE_URL}/test"
DEFAULT_QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "data", "sample_questions.jsonl")


def load_questions(path: str):
    """Yield dicts with keys id, question, expected (optional)."""
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
                print(f"Warning: line {i} has no 'question' or 'text': skipped", file=sys.stderr)
                continue
            yield {
                "id": obj.get("id", f"q{i}"),
                "question": q,
                "expected": obj.get("expected") or obj.get("expected_answer"),
            }


def normalize_answer(text: str) -> str:
    """Try to extract a single choice (A/B/C/D) from the response."""
    if not text:
        return ""
    text = text.upper().strip()
    # Common patterns: "Answer: A", "A.", "A)", "(A)", "the answer is A"
    for m in re.finditer(r"\b([A-D])\b", text):
        return m.group(1)
    return text[:1] if text else ""


def check_expected(response_text: str, expected: str) -> bool:
    if not expected:
        return None
    normalized = normalize_answer(response_text)
    exp = str(expected).strip().upper()[:1]
    return normalized == exp


def run_tests(questions_path: str, verbose: bool, output_path: str | None, limit: int | None):
    if not os.path.isfile(questions_path):
        print(f"Questions file not found: {questions_path}", file=sys.stderr)
        print("Create a JSONL file with one object per line, e.g.:", file=sys.stderr)
        print('  {"id": "1", "question": "Your question?", "expected": "A"}', file=sys.stderr)
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
        print(f"Processing {qid} ({i}/{total})... ", end="", flush=True)
        try:
            r = requests.post(TEST_ENDPOINT, json={"message": question}, timeout=120)
            r.raise_for_status()
            data = r.json()
            response_text = data.get("response", "")
        except requests.RequestException as e:
            print(f"[{qid}] ERROR: {e}", file=sys.stderr)
            err_detail = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    body = e.response.json()
                    if "detail" in body:
                        err_detail = body["detail"]
                        print(f"  Server detail: {err_detail}", file=sys.stderr)
                except Exception:
                    if e.response.text:
                        print(f"  Response: {e.response.text[:500]}", file=sys.stderr)
            results.append({"id": qid, "ok": False, "error": err_detail, "response": None})
            continue

        passed = check_expected(response_text, expected)
        results.append({
            "id": qid,
            "ok": True,
            "expected": expected,
            "passed": passed,
            "response": response_text[:2000] if response_text else "",
            "modules_used": data.get("modules_used", []),
        })

        status = ""
        if expected is not None:
            status = " PASS" if passed else " FAIL"
        print(f"[{qid}]{status}")
        if verbose:
            print(f"  Q: {question[:200]}{'...' if len(question) > 200 else ''}")
            print(f"  A: {response_text[:500]}{'...' if len(response_text) > 500 else ''}")
            if expected is not None:
                print(f"  Expected: {expected}  Got: {normalize_answer(response_text)}")
        print()

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {output_path}")

    if any(r.get("expected") is not None for r in results):
        passed_count = sum(1 for r in results if r.get("passed") is True)
        total_with_expected = sum(1 for r in results if r.get("expected") is not None)
        print(f"Score: {passed_count}/{total_with_expected} (with expected answer)")
    return results


def main():
    parser = argparse.ArgumentParser(description="Run standardized tests via /test API")
    parser.add_argument(
        "questions_file",
        nargs="?",
        default=DEFAULT_QUESTIONS_FILE,
        help="JSONL file with questions (default: scripts/data/sample_questions.jsonl)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print full Q&A")
    parser.add_argument("-o", "--output", metavar="JSON", help="Write results to JSON file")
    parser.add_argument("-n", "--limit", type=int, metavar="N", help="Run only the first N questions (for quick checks)")
    args = parser.parse_args()
    run_tests(args.questions_file, args.verbose, args.output, args.limit)


if __name__ == "__main__":
    main()
