from flask import Flask, request
import os
import json
import joblib
import numpy as np
import pandas as pd
from bybit import bybit

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@app.route('/', methods=['GET'])
def home():
    return "Nova AI Bot is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return "Invalid data", 400

    signal = data.get("signal")
    if not signal:
        return "Missing signal", 400

    # Dummy feature example from signal
    features = np.array([
        signal.get("macd", 0),
        signal.get("stoch_rsi", 0),
        signal.get("volume", 0),
        signal.get("ema_trend", 0)
    ]).reshape(1, -1)

    model = joblib.load("nova_brain.pkl")
    confidence = model.predict_proba(features)[0][1] * 100

    if confidence >= 80:
        message = f"📈 Nova AI Signal: {signal.get('type').upper()}\nConfidence: {confidence:.2f}%"
        send_telegram_message(message)
        return "Signal sent", 200
    else:
        return "Signal ignored (low confidence)", 200

def send_telegram_message(text):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)