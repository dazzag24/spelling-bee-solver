# app/app.py
import re
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load word list
WORD_LIST_PATH = os.getenv('WORD_LIST_PATH', '/app/words.txt')
word_set = set()

def load_words():
    global word_set
    try:
        with open(WORD_LIST_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            word_set = {
                w.strip().lower()
                for w in f
                if re.fullmatch(r"[a-zA-Z]{4,}", w.strip())
            }
        print(f"✅ Loaded {len(word_set)} words.")
    except Exception as e:
        print(f"❌ Failed to load words: {e}")

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/solve", methods=["POST"])
def solve():
    center = request.json.get("center", "").strip().lower()
    outer = [c.strip().lower() for c in request.json.get("outer", [])]

    # Validate
    if len(center) != 1 or not center.isalpha():
        return jsonify({"error": "Center must be a single letter."}), 400
    if len(outer) != 6 or not all(len(c) == 1 and c.isalpha() for c in outer):
        return jsonify({"error": "Outer must be 6 single letters."}), 400

    allowed = set(outer + [center])
    valid = []

    for word in word_set:
        if len(word) < 4:
            continue
        if not set(word).issubset(allowed):
            continue
        if center not in word:
            continue
        valid.append(word)

    valid.sort(key=lambda w: (len(w), w))
    return jsonify({
        "words": valid,
        "count": len(valid),
        "pangrams": [w for w in valid if set(w) == allowed]
    })

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    if not hasattr(app, 'all_words'):
        return jsonify([])
    return jsonify([w for w in app.all_words if w.startswith(query)])

with app.app_context():
    print("🧠 Loading word list...")
    load_words()
    print("✅ Word list loaded. Server ready!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)