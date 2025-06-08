from flask import Flask, request
import requests
import datetime

app = Flask(__name__)

# Deine Zugangsdaten
INFLUX_URL = "https://influx-prod-24-prod-eu-west-2.grafana.net"
INFLUX_USERNAME = "2486387"
INFLUX_TOKEN = "glc_eyJvIjoiMTQ1MTIzNCIsIm4iOiJzdGFjay0xMjgxMDc2LWluZmx1eC13cml0ZS1rYXRvdW5hX3Rva2VuIiwiayI6IjIxMTNnV1E3NldtMjhJUmxNVHMwRDNGRyIsIm0iOnsiciI6InByb2QtZXUtd2VzdC0yIn19"
BUCKET = "default"
ORG = "main"

# Die genaue Write-URL für Influx-kompatibles Senden
WRITE_URL = f"{INFLUX_URL}/api/v2/write?bucket={BUCKET}&org={ORG}&precision=s"

@app.route("/shelly", methods=["GET"])
def receive_data():
    temp = request.args.get("temp")

    if temp is None:
        return "Missing 'temp' query parameter", 400

    try:
        temperature = float(temp)
    except ValueError:
        return "Invalid 'temp' value", 400

    # InfluxDB Line Protocol Format
    line = f"pool_temperature value={temperature} {int(datetime.datetime.utcnow().timestamp())}"

    headers = {
        "Authorization": f"Token {INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    response = requests.post(WRITE_URL, headers=headers, data=line)

    if response.status_code == 204:
        return "OK", 200
    else:
        return f"Error from InfluxDB: {response.text}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
