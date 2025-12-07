# app.py
import os
import sqlite3
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from utils import (
    call_openrouter,
    build_prompt_for_action,
    check_local_repetition,
    check_web_plagiarism
)

# Load config
if os.path.exists("config.txt"):
    with open("config.txt", "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
DB_NAME = "wordcraft.db"

# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                original_text TEXT,
                result_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

init_db()

def save_to_history(action, original, result):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO history (action, original_text, result_text) VALUES (?, ?, ?)",
                (action, original, result)
            )
    except Exception as e:
        print(f"DB Error: {e}")

# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")

    action = request.form.get("action")
    text = request.form.get("text", "").strip()
    tone = request.form.get("tone", "Professional")

    if not text:
        flash("Please enter some text.", "warning")
        return redirect(url_for("home"))

    # API Config
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "mistralai/mistral-nemo:free")

    if not api_key:
        return render_template("index.html", result="Error: API Key missing in config.txt", original_text=text)

    # Generate Prompt
    prompt = build_prompt_for_action(action, text, tone)
    
    # Call AI
    result = call_openrouter(prompt, api_key, model)

    # Save to History (only if successful)
    if "Error" not in result:
        save_to_history(action, text, result)

    return render_template("index.html", result=result, original_text=text, action=action)

@app.route("/plagiarism_check", methods=["POST"])
def plagiarism_api():
    text = request.form.get("text", "")
    mode = request.form.get("mode", "local") # 'local' or 'web'
    
    if mode == "web":
        report = check_web_plagiarism(text)
    else:
        report = check_local_repetition(text)
        
    return jsonify(report)

@app.route("/history")
def history():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 20").fetchall()
        return render_template("history.html", rows=rows)
    except Exception as e:
        return f"Database error: {e}"

if __name__ == "__main__":
    app.run(debug=False, port=5000)
