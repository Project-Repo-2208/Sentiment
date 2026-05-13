from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "meta-llama/llama-3-8b-instruct:free"

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "Running"
    })

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":

        return jsonify({
            "message": "Webhook endpoint is active"
        })

    try:

        data = request.json

        texts = []

        response_set = data.get("responseSet", [])

        for question in response_set:

            answer_values = question.get("answerValues", [])

            for answer in answer_values:

                value = answer.get("value", {})

                extracted_text = value.get("text", "").strip()

                if extracted_text and extracted_text.upper() != "N/A":

                    texts.append(extracted_text)

        text = " ".join(texts)

        if not text:

            return jsonify({
                "success": False,
                "message": "No valid text responses found"
            }), 400

        prompt = f"""
You are a sentiment analysis engine.

Analyze the sentiment of the following survey response.

Rules:
- Return ONLY one word
- Positive
- Negative
- Neutral

Survey Response:
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
            "responseID": data.get("responseID"),
            "surveyID": data.get("surveyID"),
            "surveyName": data.get("surveyName"),
            "textAnalyzed": text,
            "sentiment": sentiment
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
