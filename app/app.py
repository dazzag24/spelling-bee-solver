from flask import Flask, render_template, request, jsonify
import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.async_api import async_playwright

app = Flask(__name__)

word_set = set()
letters = []
center_letter = ""

async def fetch_spellbee_data():
    global word_set, letters
    today = datetime.now().strftime("%Y-%m-%d")
    url = "https://spellbee.org/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        # Get today's letters
        letters_js = f'window.games["{today}"].data.letters'
        center_letters_js = f'window.games["{today}"].data.center_letter'
        dictionary_js = f'window.games["{today}"].data.dictionary'
        try:
            center_letter = await page.evaluate(center_letters_js)
            if not center_letter or not isinstance(center_letter, str) or len(center_letter) != 1:
                print(f"❌ No center letter found for {today}")
                center_letter = ""
            else:
                print(f"✅ Loaded center letter for {today}: {center_letter}")
            letters = await page.evaluate(letters_js)
            if not letters or len(letters) != 7:
                print(f"❌ No letters found for {today}")
                letters = []
            else:
                print(f"✅ Loaded letters for {today}: {letters}")
            dictionary = await page.evaluate(dictionary_js)
            if not dictionary:
                print(f"❌ No dictionary found for {today}")
                word_set = set()
            else:
                word_set = set(w.lower() for w in dictionary if isinstance(w, str) and len(w) >= 4)
                print(f"✅ Loaded {len(word_set)} words for {today}")
        except Exception as e:
            print(f"❌ Failed to fetch data: {e}")
            word_set = set()
        await browser.close()

def schedule_spellbee_fetch():
    loop = asyncio.get_event_loop()
    loop.create_task(fetch_spellbee_data())

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(fetch_spellbee_data()), 'cron', hour=1, minute=0)
scheduler.start()

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/solve", methods=["POST"])
def solve():
    global letters
    if not letters or len(letters) != 7:
        return jsonify({"error": "Letters not loaded yet."}), 503

    data = request.get_json() or {}
    prefix = (data.get("prefix") or "").lower().strip()

    if not prefix or len(prefix) < 2:
        return jsonify({"error": "Please enter at least 2 starting letters."}), 400

    center = letters[0].lower()
    allowed = set(letters)
    valid = []

    for word in word_set:
        if len(word) < 4:
            continue
        if not set(word).issubset(allowed):
            continue
        if center not in word:
            continue
        if not word.startswith(prefix):
            continue
        valid.append(word)

    valid.sort(key=lambda w: (len(w), w))
    return jsonify({
        "words": valid,
        "count": len(valid),
        "pangrams": [w for w in valid if set(w) == allowed]
    })

@app.route("/letters")
def get_letters():
    global letters
    return jsonify({"letters": letters})

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    if not hasattr(app, 'all_words'):
        return jsonify([])
    return jsonify([w for w in app.all_words if w.startswith(query)])

with app.app_context():
    print("🧠 Fetching today's SpellBee data...")
    asyncio.run(fetch_spellbee_data())
    print("✅ SpellBee data loaded. Server ready!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)