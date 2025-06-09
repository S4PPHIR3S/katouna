from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

# Korrekte InfluxDB v2 Write URL von Grafana Cloud (Pfad + Query-Parameter!)
WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v2/write?bucket=default&org=main&precision=s"

# API Token aus ENV-Variable oder direkt hier (für Sicherheit ENV empfohlen)
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "dein_grafana_api_token"

# --------------------------
# Shelly Webhook-Route (GET und POST)
# --------------------------

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    # Temperatur aus Query-Param (GET) oder Form-Daten (POST)
    temp_param = request.args.get("temp") or request.form.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp())

    # InfluxDB Line Protocol Format
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8"
    }

    try:
        response = requests.post(WRITE_URL, data=line, headers=headers)
        print(f"Sent: {line}")
        print(f"Response {response.status_code}: {response.text}")
        if response.status_code == 204:
            return "OK", 200
        else:
            return f"InfluxDB write failed: {response.status_code} {response.text}", 500
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

# --------------------------
# Render / Railway Startup
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
