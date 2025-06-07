# datei: webhook_server.py
from flask import Flask, request
import requests
import time

# Grafana Cloud / InfluxDB Konfiguration
INFLUX_URL = "https://<dein-endpunkt>.grafana.net/api/v2/write?org=<deine-org>&bucket=<dein-bucket>&precision=s"
INFLUX_TOKEN = "<dein-token>"

app = Flask(__name__)

@app.route("/shelly", methods=["GET"])
def receive_temp():
    temp = request.args.get("temp")
    if temp:
        payload = f"pool_temperature value={temp} {int(time.time())}"
        headers = {
            "Authorization": f"Token {INFLUX_TOKEN}",
            "Content-Type": "text/plain"
        }
        r = requests.post(INFLUX_URL, headers=headers, data=payload)
        return f"OK: {r.status_code}", r.status_code
    return "Fehlender Temperaturwert", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
