from flask import Flask, request

app = Flask(__name__)

@app.route("/shelly", methods=["GET", "POST"])
def shelly_webhook():
    temp_param = request.args.get("temp") or request.form.get("temp")
    try:
        temperature = float(temp_param)
    except (TypeError, ValueError):
        return "Missing or invalid 'temp' parameter", 400

    print(f"Received temperature: {temperature}")

    # Einfach OK zurückgeben mit 200 Status
    return f"Received temperature: {temperature}", 200

@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
