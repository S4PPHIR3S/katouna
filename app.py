@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    temp_param_pool = request.args.get("temp_pool") or request.form.get("temp_pool")
    temp_param_air = request.args.get("temp_air") or request.form.get("temp_air")
    try:
        temperature_pool = float(temp_param_pool)
        temperature_air = float(temp_param_air)
    except (TypeError, ValueError):
        return "Missing or invalid 'temps' parameter", 400

    timestamp = int(datetime.datetime.utcnow().timestamp() * 1e9)

    line_pool = f"pool_temperature,sensor=pool value={temperature_pool} {timestamp}"
    line_air = f"air_temperature,sensor=air value={temperature_air} {timestamp}"

    headers = {
        "Authorization": f"Bearer {INFLUX_USER}:{INFLUX_TOKEN}",
        "Content-Type": "text/plain"
    }

    try:
        resp1 = requests.post(WRITE_URL, data=line_pool, headers=headers)
        print(f"Sent: {line_pool}")
        print(f"Response {resp1.status_code}: {resp1.text}")

        resp2 = requests.post(WRITE_URL, data=line_air, headers=headers)
        print(f"Sent: {line_air}")
        print(f"Response {resp2.status_code}: {resp2.text}")

        if resp1.ok and resp2.ok:
            return f"Received temperatures: pool:{temperature_pool}, air:{temperature_air}", 200
        else:
            return "InfluxDB write failed", 500
    except Exception as e:
        print(f"Exception: {e}")
        return "Error", 500
