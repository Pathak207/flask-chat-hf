from flask import Flask, request, jsonify
from openai import OpenAI
import os
from datetime import datetime
import pytz
import requests

app = Flask(__name__)

# 🔹 Environment variables
HF_TOKEN = os.environ.get("HF_TOKEN")
CRICAPI_KEY = os.environ.get("CRICAPI_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set!")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# ----------------- Utility functions ----------------- #

def get_current_datetime():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    date_str = now.strftime("%d %B %Y")
    day_str = now.strftime("%A")
    time_str = now.strftime("%H:%M:%S")
    return f"Aaj ki tareekh hai: {date_str} ({day_str}) aur samay hai: {time_str}"

def get_live_cricket_score():
    if not CRICAPI_KEY:
        return "Cricket API key missing."
    url = f"https://cricapi.com/api/matches?apikey={CRICAPI_KEY}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        matches = data.get("matches", [])
        live_matches = [m for m in matches if m.get("matchStarted") and not m.get("matchEnded")]

        if not live_matches:
            return "Aaj koi live cricket match nahi hai."

        scores = []
        for match in live_matches[:3]:  # top 3 live matches
            team1 = match.get("team-1")
            team2 = match.get("team-2")
            score = match.get("score", "Score update nahi hai")
            status = match.get("matchStatus", "")
            scores.append(f"• {team1} vs {team2}: {score} ({status})")

        return "Live Cricket Scores:\n" + "\n".join(scores)
    except Exception as e:
        return f"Cricket score fetch karte waqt error: {e}"

def get_live_news():
    if not NEWS_API_KEY:
        return "News API key missing."
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get("articles", [])[:5]
        if not articles:
            return "Aaj koi news update nahi hai."

        news_list = [f"• {a['title']}" for a in articles]
        return "Aaj ki khaas khabrein:\n" + "\n".join(news_list)
    except Exception as e:
        return f"News fetch karte waqt error: {e}"

# ----------------- Main route ----------------- #

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    try:
        print(f"💬 Received prompt: {prompt}")

        # 🔹 Special real-time commands
        if "date" in prompt.lower() or "time" in prompt.lower():
            response = get_current_datetime()
        elif "cricket" in prompt.lower() or "score" in prompt.lower():
            response = get_live_cricket_score()
        elif "news" in prompt.lower() or "khabrein" in prompt.lower():
            response = get_live_news()
        else:
            # 🔹 AI model response
            completion = client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905",
                messages=[{"role": "user", "content": prompt}]
            )
            response = completion.choices[0].message.content

        print(f"✅ Generated response: {response}")
        return jsonify({"response": response})

    except Exception as e:
        print(f"❌ Exception: {e}")
        return jsonify({"error": str(e)}), 500

# ----------------- Run server ----------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
