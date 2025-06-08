from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v2/write"
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "DEIN_GRAFANA_TOKEN"
BUCKET = "default"
ORG = "main"

# --------------------------
# Webhook-Route für Shelly
# --------------------------

@app.route("/shelly", methods=["GET"])
def shelly_webhook():
    temp_param = request.args.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp())
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    params = {
        "bucket": BUCKET,
        "org": ORG,
        "precision": "s"
    }

    try:
        response = requests.post(WRITE_URL, params=params, data=line, headers=headers)
        print(f"Sent: {line}")
        print(f"Response {response.status_code}: {response.text}")
        return "OK", response.status_code
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

# --------------------------
# Testroute
# --------------------------

@app.route("/ping")
def ping():
    return "pong", 200

# --------------------------
# Render Start
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
