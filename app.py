from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# --------------------------
# Konfiguration
# --------------------------

# Influx Write Endpoint (Grafana Cloud oder eigener Server)
WRITE_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v1/push/influx/write"

# Instance ID und Token (aus Umgebungsvariablen oder fest gesetzt)
INFLUX_USER = os.getenv("INFLUX_USER") or "2486387"
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") or "dein_token_hier"  # ← anpassen!

# --------------------------
# Shelly Webhook-Route
# --------------------------

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    temp_param_pool = request.args.get("temp_pool") or request.form.get("temp_pool")
    temp_param_air = request.args.get("temp_air") or request.form.get("temp_air")

    timestamp = int(datetime.datetime.utcnow().timestamp() * 1e9)  # nanosekunden
    headers = {
        "Authorization": f"Bearer {INFLUX_USER}:{INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    errors = []
    results = []

    # Pool-Temperatur senden
    if temp_param_pool:
        try:
            temperature_pool = float(temp_param_pool)
            line_pool = f"pool_temperature,sensor=pool value={temperature_pool} {timestamp}"
            resp = requests.post(WRITE_URL, data=line_pool, headers=headers)
            print(f"Sent: {line_pool}")
            if resp.ok:
                results.append(f"pool={temperature_pool}")
            else:
                errors.append(f"Influx error (pool): {resp.status_code}")
        except Exception as e:
            print(f"Exception (pool): {e}")
            errors.append("Exception (pool)")

    # Luft-Temperatur senden
    if temp_param_air:
        try:
            temperature_air = float(temp_param_air)
            line_air = f"air_temperature,sensor=air value={temperature_air} {timestamp}"
            resp = requests.post(WRITE_URL, data=line_air, headers=headers)
            print(f"Sent: {line_air}")
            if resp.ok:
                results.append(f"air={temperature_air}")
            else:
                errors.append(f"Influx error (air): {resp.status_code}")
        except Exception as e:
            print(f"Exception (air): {e}")
            errors.append("Exception (air)")

    # Rückgabe
    if not results:
        return "Missing or invalid temperature parameters", 400
    if errors:
        return f"Partial success: {' | '.join(results)} | Errors: {' | '.join(errors)}", 207

    return f"Received: {', '.join(results)}", 200

# --------------------------
# Health Check
# --------------------------

@app.route("/ping")
def ping():
    return "pong", 200

# --------------------------
# Startpunkt
# --------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
