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
