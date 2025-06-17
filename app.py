from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

# Influx Write Endpoint für Grafana Cloud mit Push-Support
WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v1/push/influx/write"

# User-ID (Instance ID) und Token (Access Policy)
INFLUX_USER = os.getenv("INFLUX_USER") or "2486387"  # Deine Instance ID
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "dein_token_hier"

# --------------------------
# Webhook-Route für Shelly (GET + POST)
# --------------------------

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    # Temperatur abrufen
    temp_param = request.args.get("temp") or request.form.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp() * 1e9)  # Influx erwartet Nanosekunden

    # Influx Line Protocol mit Messung und Tag
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Bearer {INFLUX_USER}:{INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    try:
        response = requests.post(WRITE_URL, data=line, headers=headers)
        print(f"Sent: {line}")
        print(f"Response {response.status_code}: {response.text}")
        return f"Received temperature: {temperature}", response.status_code
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

# Optional: Health Check
@app.route("/ping")
def ping():
    return "pong", 200

# --------------------------
# Entry Point
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
