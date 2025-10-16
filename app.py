from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# 🔹 Hugging Face token (server-side safe)
HF_TOKEN = os.environ.get(
    "HF_TOKEN",
    "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"
)

# 🔹 OpenAI client via Hugging Face
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    try:
        # 🔹 Chat completion
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[{"role": "user", "content": prompt}]
        )

        # 🔹 FIXED: use .content instead of .get()
        message = completion.choices[0].message.content

        return jsonify({"response": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 0.0.0.0 -> emulator/other devices can access it
    # 🔹 Port 5001 (to avoid conflict with 5000)
    app.run(host="0.0.0.0", port=5001, debug=True)
