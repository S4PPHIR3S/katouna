from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --- Konfiguration ---

# InfluxDB Write URL mit api/v2/write, Bucket, Org und Präzision (Sekunden)
INFLUX_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v2/write"
BUCKET = "default"
ORG = "main"

# Dein Grafana Cloud Token (am besten als ENV-Variable setzen)
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "dein_grafana_token"

# Vollständige Write-URL mit Query-Parametern
WRITE_URL = f"{INFLUX_URL}?bucket={BUCKET}&org={ORG}&precision=s"

# --- Route für Shelly Webhook ---

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    # Temperatur aus GET Query oder POST Form auslesen
    temp_param = request.args.get("temp") or request.form.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    # Aktueller Zeitstempel in Sekunden UTC
    timestamp = int(datetime.datetime.utcnow().timestamp())

    # Influx Line Protocol: Messung 'pool_temperature', Tag sensor=pool, Feld value
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    # Daten an InfluxDB senden
    response = requests.post(WRITE_URL, data=line, headers=headers)

    if response.status_code == 204:
        # 204 No Content = Erfolg beim Schreiben in InfluxDB
        print(f"Sent to InfluxDB: {line}")
        return f"Received temperature: {temperature}", 200
    else:
        print(f"InfluxDB write failed: {response.status_code} {response.text}")
        return "Failed to write to InfluxDB", 500

# --- Hauptprogramm ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
