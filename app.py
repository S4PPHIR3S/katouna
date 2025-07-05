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
    # Temperaturen abrufen
    temp_param_pool = request.args.get("temp_pool") or request.form.get("temp_pool")
    temp_param_air = request.args.get("temp_air") or request.form.get("temp_air")
    try:
        temperature_pool = float(temp_param_pool)
        temperature_air = float(temp_param_air)
    except (TypeError, ValueError):
        return "Missing or invalid 'temps' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp() * 1e9)  # Influx erwartet Nanosekunden

    # Influx Line Protocol mit Messung und Tag
    line_pool = f"pool_temperature,sensor=pool value={temperature_pool} {timestamp}"

    line_air = f"air_temperature,sensor=air value={temperature_air} {timestamp}"

    headers = {
        "Authorization": f"Bearer {INFLUX_USER}:{INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    try:
        response = requests.post(WRITE_URL, data=line_pool, headers=headers)
        print(f"Sent: {line_pool}")
        print(f"Response {response.status_code}: {response.text}")
        return f"Received temperatures: pool:{temperature_pool}", response.status_code
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

    
    try:
        response = requests.post(WRITE_URL, data=line_air, headers=headers)
        print(f"Sent: {line_air}")
        print(f"Response {response.status_code}: {response.text}")
        return f"Received temperatures: air:{temperature_air}", response.status_code
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
