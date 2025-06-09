from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# Optional: Ping-Route für Test
@app.route("/ping")
def ping():
    return "pong", 200

# Webhook-Route für Shelly (GET erlaubt)
@app.route("/shelly", methods=["GET"])
def shelly():
    temp = request.args.get("temp")
    if not temp:
        return "Missing temperature", 400

    try:
        temperature = float(temp)
    except ValueError:
        return "Invalid temperature", 400

    timestamp = int(datetime.datetime.utcnow().timestamp())
    line = f"pool_temperature,sensor=pool value={temperature} {timestamp}"

    headers = {
        "Authorization": f"Token {os.getenv('INFLUX_TOKEN') or 'DEIN_TOKEN_HIER'}",
        "Content-Type": "text/plain"
    }

    params = {
        "bucket": "default",
        "org": "main",
        "precision": "s"
    }

    response = requests.post(
        "https://influx-prod-24-prod-eu-west-2.grafana.net/api/v2/write",
        params=params,
        data=line,
        headers=headers
    )

    print(f"Sent line: {line}")
    print(f"Influx response: {response.status_code} - {response.text}")

    return "OK", response.status_code

# Für Render-Deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
