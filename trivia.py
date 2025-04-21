#!/usr/bin/env python3
"""
daily‑trivia: pull one multiple‑choice question from OpenTDB and quiz the user.
"""
import requests, json, pathlib, random, html, sys

CACHE = pathlib.Path(".cache.json")
API = "https://opentdb.com/api.php?amount=5&type=multiple"

def fetch_fresh_batch():
    r = requests.get(API, timeout=5)
    r.raise_for_status()
    return r.json()["results"]

def next_question():
    if CACHE.exists():
        buf = json.loads(CACHE.read_text())
    else:
        buf = fetch_fresh_batch()
    if not buf:
        buf = fetch_fresh_batch()      # exhausted cache → refresh
    q = buf.pop(0)
    CACHE.write_text(json.dumps(buf))
    return q

def quiz(q):
    print("\n\u001b[1m" + html.unescape(q["question"]) + "\u001b[0m")
    answers = q["incorrect_answers"] + [q["correct_answer"]]
    random.shuffle(answers)
    for i, ans in enumerate(answers, 1):
        print(f"  {i}. {html.unescape(ans)}")
    choice = input("\nYour guess (1‑4): ")
    try:
        pick = answers[int(choice) - 1]
    except (ValueError, IndexError):
        sys.exit("💥  Invalid choice. Rage‑quit.")
    if html.unescape(pick) == html.unescape(q["correct_answer"]):
        print("✅  Correct!\n")
    else:
        print(f"❌  Nope. Answer was: {q['correct_answer']}\n")

if __name__ == "__main__":
    quiz(next_question())
# top of trivia.py
import argparse
DEFAULT_API = "https://opentdb.com/api.php"

def parse_args():
    p = argparse.ArgumentParser(description="Daily trivia CLI")
    p.add_argument("-c", "--category", type=int, help="OpenTDB category ID")
    p.add_argument("-d", "--difficulty", choices=["easy", "medium", "hard"])
    p.add_argument("-n", "--amount", type=int, default=1, help="# of questions")
    p.add_argument("--no-cache", action="store_true", help="Ignore local cache")
    return p.parse_args()
DEFAULT_API = "https://opentdb.com/api.php"

def fetch_fresh_batch(args):
    """
    Pull a batch of questions from OpenTDB based on user flags.
    We stick to multiple‑choice ('type=multiple') so the quiz UI stays simple.
    """
    params = {
        "amount": args.amount,
        "type":   "multiple",
    }
    if args.category:
        params["category"] = args.category
    if args.difficulty:
        params["difficulty"] = args.difficulty

    r = requests.get(DEFAULT_API, params=params, timeout=5)
    r.raise_for_status()
    return r.json()["results"]
CACHE = pathlib.Path(".cache.json")

def next_question(args):
    # blow away cache if user asked for fresh pull
    if args.no_cache and CACHE.exists():
        CACHE.unlink()

    if CACHE.exists():
        buf = json.loads(CACHE.read_text())
    else:
        buf = fetch_fresh_batch(args)

    if not buf:                 # Cache exhausted
        buf = fetch_fresh_batch(args)

    q = buf.pop(0)
    CACHE.write_text(json.dumps(buf, indent=2))
    return q
if __name__ == "__main__":
    args = parse_args()
    quiz(next_question(args))
# inside next_question(args):
else:
    buf = fetch_fresh_batch(args)   # ← args must be forwarded here
