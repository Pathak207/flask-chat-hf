from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# 🔹 Hugging Face token from environment (Render secret)
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set!")

# 🔹 OpenAI client via Hugging Face
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

        # 🔹 Chat completion call
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[{"role": "user", "content": prompt}]
        )

        # 🔹 Extract response safely
        message = completion.choices[0].message.content
        print(f"✅ Generated response: {message}")

        return jsonify({"response": message})

    except Exception as e:
        print(f"❌ Exception: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 🔹 Dynamic port from environment (Render provides PORT)
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
