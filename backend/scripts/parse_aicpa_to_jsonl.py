#!/usr/bin/env python3
"""
Parse AICPA-style questions: each block ends with a line "X. answer" (X = A-D).
Output JSONL with id, question (everything except last line), expected (the letter).
Reads from stdin or first argument filename.
"""
import json
import re
import sys

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Split on double newline; then merge consecutive fragments until we have a block
    # that ends with an answer line (A. B. C. or D.). Some questions have \n\n between stem and options.
    raw_blocks = re.split(r"\n\s*\n", text)
    answer_line_re = re.compile(r"^([A-D])\.\s+", re.IGNORECASE)
    merged = []
    current = []
    for b in raw_blocks:
        b = b.strip()
        if not b:
            continue
        current.append(b)
        combined = "\n\n".join(current)
        lines = [ln.strip() for ln in combined.split("\n") if ln.strip()]
        # Count lines that are answer-style (A. or B. or C. or D.); need at least 5 (4 options + 1 answer)
        choice_lines = sum(1 for ln in lines if answer_line_re.match(ln))
        if choice_lines >= 5 and lines:
            merged.append(combined)
            current = []
    out = []
    n = 0
    for block in merged:
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        answer_idx = None
        for i in range(len(lines) - 1, -1, -1):
            if answer_line_re.match(lines[i]):
                answer_idx = i
                break
        if answer_idx is None:
            continue
        last = lines[answer_idx]
        match = answer_line_re.match(last)
        expected = match.group(1).upper()
        question_text = "\n".join(lines[:answer_idx]).strip()
        n += 1
        out.append({
            "id": f"q{n:02d}",
            "question": question_text,
            "expected": expected,
        })

    for rec in out:
        print(json.dumps(rec, ensure_ascii=False))

if __name__ == "__main__":
    main()
