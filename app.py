from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Environment Variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter Configuration
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# You can change the model if needed
MODEL = "openai/gpt-4o-mini"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        # Incoming text from webhook
        # Change this key based on your incoming payload
        text = data.get("text", "")

        if not text:
            return jsonify({
                "success": False,
                "message": "No text provided"
            }), 400

        prompt = f"""
You are a sentiment analysis engine.

Analyze the sentiment of the following text.

Rules:
- Return ONLY one word
- Positive
- Negative
- Neutral

Text:
{text}
"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0
        }

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        sentiment = (
            result["choices"][0]["message"]["content"]
            .strip()
        )

        return jsonify({
            "success": True,
            "input_text": text,
            "sentiment": sentiment
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Running"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
