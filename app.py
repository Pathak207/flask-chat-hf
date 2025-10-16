from flask import Flask, request, jsonify
from openai import OpenAI
import os
from datetime import datetime
import pytz  # pip install pytz

app = Flask(__name__)

# Hugging Face token from environment
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set!")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    try:
        print(f"💬 Received prompt: {prompt}")

        # 🔹 Real-time date/time handling
        if "date" in prompt.lower() or "time" in prompt.lower():
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)

            date_str = now.strftime("%d %B %Y")       # 16 October 2025
            day_str = now.strftime("%A")              # Thursday
            time_str = now.strftime("%H:%M:%S")      # 10:45:14

            # Roman Hindi output
            response = f"Aaj ki tareekh hai: {date_str} ({day_str}) aur samay hai: {time_str}"
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)

