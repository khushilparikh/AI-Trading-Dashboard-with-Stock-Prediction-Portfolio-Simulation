import requests
import os

# ==============================
# CONFIG (SECURE WAY)
# ==============================
BOT_TOKEN = os.getenv("8374040580:AAFhz2HX2QoSBA13JYmA-tYYWV2brFsuI4A")
CHAT_ID = os.getenv("740392380")


# ==============================
# SEND MESSAGE
# ==============================
def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("[TELEGRAM ERROR] Missing BOT_TOKEN or CHAT_ID")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        response = requests.post(url, data=payload, timeout=5)

        if response.status_code != 200:
            print(f"[TELEGRAM ERROR] Failed: {response.text}")

    except Exception as e:
        print(f"[TELEGRAM ERROR]: {e}")


# ==============================
# ALERT TRIGGER (IMPROVED)
# ==============================
def send_alert(signal, confidence, symbol, price):

    if signal not in ["BUY", "SELL"]:
        return

    if confidence < 70:
        return

    try:
        price = round(float(price), 2)
    except:
        price = 0

    if signal == "BUY":
        msg = (
            f"🟢 *BUY SIGNAL*\n"
            f"Stock: {symbol}\n"
            f"Price: ₹{price}\n"
            f"Confidence: {confidence}%"
        )

    else:
        msg = (
            f"🔴 *SELL SIGNAL*\n"
            f"Stock: {symbol}\n"
            f"Price: ₹{price}\n"
            f"Confidence: {confidence}%"
        )

    send_telegram_message(msg)