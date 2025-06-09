from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Grafana Cloud InfluxDB Konfiguration
# --------------------------

INFLUX_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v2/write"
BUCKET = "default"       # Bucket aus Grafana Cloud (eventuell anpassen)
ORG = "main"             # Org aus Grafana Cloud (eventuell anpassen)
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")  # Dein Token als Umgebungsvariable setzen!

# --------------------------
# Route zum Empfangen der Temperaturdaten
# --------------------------

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    temp_param = request.args.get("temp") or request.form.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp())

    # InfluxDB Line Protocol format
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8"
    }

    params = {
        "bucket": BUCKET,
        "org": ORG,
        "precision": "s"
    }

    try:
        response = requests.post(INFLUX_URL, params=params, data=line, headers=headers)
        if response.status_code != 204:
            print(f"InfluxDB write failed: {response.status_code} {response.text}")
            return f"InfluxDB write failed: {response.status_code}", 500
        print(f"Sent to InfluxDB: {line}")
    except Exception as e:
        print(f"Exception sending to InfluxDB: {e}")
        return "Error sending to InfluxDB", 500

    return f"Received temperature: {temperature}", 200

@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
