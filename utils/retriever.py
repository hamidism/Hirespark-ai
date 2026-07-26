import json
import os
import re

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bullet_corpus.json")

with open(CORPUS_PATH, "r") as f:
    CORPUS = json.load(f)

def _tokenize(text):
    return set(re.findall(r"[a-z]+", text.lower()))

def retrieve_examples(query_text, top_k=3):
    """Retrieve the most relevant strong bullet examples for a given issue/problem text."""
    query_tokens = _tokenize(query_text)
    scored = []

    for entry in CORPUS:
        entry_tokens = _tokenize(entry["text"] + " " + entry["category"])
        overlap = len(query_tokens & entry_tokens)
        scored.append((overlap, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [entry["text"] for score, entry in scored[:top_k] if score > 0]

    # fallback: if nothing matched by keyword, just return a few varied examples
    if not top:
        top = [entry["text"] for entry in CORPUS[:top_k]]

    return top