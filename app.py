from flask import Flask, request
import requests
import datetime
import os

# Flask-App initialisieren (sehr wichtig!)
app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v1/push/influx/write"
INFLUX_USER = os.getenv("INFLUX_USER") or "2486387"
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "dein_token_hier"

# --------------------------
# Webhook-Route
# --------------------------

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    temp_param_pool = request.args.get("temp_pool") or request.form.get("temp_pool")
    temp_param_air = request.args.get("temp_air") or request.form.get("temp_air")
    try:
        temperature_pool = float(temp_param_pool)
        temperature_air = float(temp_param_air)
    except (TypeError, ValueError):
        return "Missing or invalid 'temps' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp() * 1e9)
    line_pool = f"pool_temperature,sensor=pool value={temperature_pool} {timestamp}"
    line_air = f"air_temperature,sensor=air value={temperature_air} {timestamp}"

    headers = {
        "Authorization": f"Bearer {INFLUX_USER}:{INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    try:
        resp1 = requests.post(WRITE_URL, data=line_pool, headers=headers)
        resp2 = requests.post(WRITE_URL, data=line_air, headers=headers)

        if resp1.ok and resp2.ok:
            return f"Received temperatures: pool:{temperature_pool}, air:{temperature_air}", 200
        else:
            return f"Error from InfluxDB: {resp1.status_code} / {resp2.status_code}", 500
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

# Optionaler Health-Check
@app.route("/ping")
def ping():
    return "pong", 200

# --------------------------
# Entry Point
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
