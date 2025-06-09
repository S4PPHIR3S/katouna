from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

# Influx-kompatibler Write Endpoint von Grafana Cloud (v2 API)
WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v2/write"
BUCKET = "default"
ORG = "main"

# Token aus ENV-Variable oder direkt hier einsetzen (empfohlen: als ENV setzen in Railway)
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "DEIN_GRAFANA_TOKEN_HIER"

# --------------------------
# Webhook-Route für Shelly (GET und POST erlauben)
# --------------------------

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    temp_param = request.args.get("temp") or request.form.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp())

    # Influx Line Protocol
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
        return f"Received temperature: {temperature}", response.status_code
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

# --------------------------
# Zum Testen, ob App läuft
# --------------------------

@app.route("/ping")
def ping():
    return "pong"

# --------------------------
# Railway benötigt das hier
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
