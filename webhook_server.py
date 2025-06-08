from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

# Influx-kompatibler Write Endpoint von Grafana Cloud (nicht api/v2!)
WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net"

# Aus Grafana Cloud → "Username / Instance ID" → als ENV-Variable speichern oder hier direkt setzen
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "dein_grafana_token"

# --------------------------
# Webhook-Route für Shelly
# --------------------------

@app.route("/shelly")
def shelly_webhook():
    try:
        temperature = float(request.args.get("temp"))
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp())
    
    # Influx Line Protocol → mit sensor-Label für Prometheus
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    # Sende Daten an Grafana Cloud
    try:
        response = requests.post(WRITE_URL, data=line, headers=headers)
        print(f"Sent: {line}")
        print(f"Response {response.status_code}: {response.text}")
        return "OK", response.status_code
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500

# --------------------------
# Render benötigt das hier
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
