import os
import threading
import requests
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Read a file safely
def read_file(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as file:
        return [line.strip() for line in file.readlines()]

# Run the script
def send_messages_from_file():
    start_time = datetime.now()
    convo_id = read_file(os.path.join(UPLOAD_FOLDER, "convo.txt"))[0] if read_file(os.path.join(UPLOAD_FOLDER, "convo.txt")) else None
    messages = read_file(os.path.join(UPLOAD_FOLDER, "NP.txt"))
    tokens = read_file(os.path.join(UPLOAD_FOLDER, "tokennum.txt"))
    hatters_names = read_file(os.path.join(UPLOAD_FOLDER, "hattersname.txt"))
    speed = int(read_file(os.path.join(UPLOAD_FOLDER, "time.txt"))[0]) if read_file(os.path.join(UPLOAD_FOLDER, "time.txt")) else 5

    if not convo_id or not messages or not tokens or not hatters_names:
        return "[Error] Missing required data files."

    message_count = 0

    try:
        while True:
            for i, message in enumerate(messages):
                token = tokens[i % len(tokens)]
                hater_name = hatters_names[i % len(hatters_names)]
                full_message = f"{hater_name} {message}"

                url = f"https://graph.facebook.com/v17.0/t_{convo_id}/"
                response = requests.post(url, json={"access_token": token, "message": full_message})

                message_count += 1
                if response.ok:
                    print(f"[✔] Sent ({message_count}): {hater_name}: {message}")
                else:
                    print(f"[x] Failed ({message_count}): {hater_name}: {message}")

                time.sleep(speed)

    except Exception as e:
        print(f"[!] Error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    return redirect(url_for("index"))

@app.route("/start-script", methods=["POST"])
def start_script():
    thread = threading.Thread(target=send_messages_from_file, daemon=True)
    thread.start()
    return jsonify({"status": "Script started successfully!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)