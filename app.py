from flask import Flask, render_template, request, redirect, url_for, flash, Response
from datetime import datetime
from collections import Counter
import csv, io, json, os, base64
import cv2
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
ATTENDANCE = os.path.join(DATA, "attendance.csv")
SESSIONS = os.path.join(DATA, "sessions.json")

app = Flask(__name__)
app.secret_key = "local-demo-key-change-before-deployment"

FIELDS = ["timestamp", "student_name", "student_id", "session", "status",
          "engagement_score", "engagement_label", "notes"]

def get_records():
    if not os.path.exists(ATTENDANCE):
        return []
    with open(ATTENDANCE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_sessions():
    try:
        with open(SESSIONS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []

def label_for(score):
    if score >= 75: return "High"
    if score >= 45: return "Moderate"
    return "Low"

@app.route("/")
def index():
    records = get_records()
    today = datetime.now().strftime("%Y-%m-%d")
    today_records = [r for r in records if r.get("timestamp", "").startswith(today)]
    scores = [int(r.get("engagement_score", 0) or 0) for r in today_records]
    avg = round(sum(scores) / len(scores)) if scores else 0
    return render_template("index.html", records=records[-10:][::-1],
        today_count=len(today_records),
        unique_students=len(set(r.get("student_id") for r in today_records)),
        avg_score=avg, sessions=get_sessions())

@app.route("/mark", methods=["POST"])
def mark():
    name = request.form.get("student_name", "").strip()
    sid = request.form.get("student_id", "").strip()
    session = request.form.get("session", "").strip() or "Demo Classroom"
    status = request.form.get("status", "Present")
    notes = request.form.get("notes", "").strip()
    try: score = max(0, min(100, int(request.form.get("engagement_score", "60"))))
    except ValueError: score = 60
    if not name or not sid:
        flash("Please enter both student name and student ID.", "error")
        return redirect(url_for("index"))
    exists = os.path.exists(ATTENDANCE)
    with open(ATTENDANCE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists: writer.writeheader()
        writer.writerow({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student_name": name, "student_id": sid, "session": session,
            "status": status, "engagement_score": score,
            "engagement_label": label_for(score), "notes": notes})
    flash("Attendance record saved locally.", "success")
    return redirect(url_for("index"))

@app.route("/session", methods=["POST"])
def add_session():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Enter a session title.", "error")
        return redirect(url_for("index"))
    sessions = get_sessions()
    sessions.append({"title": title, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
    with open(SESSIONS, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)
    flash("Session created.", "success")
    return redirect(url_for("index"))

@app.route("/analyze", methods=["POST"])
def analyze():
    upload = request.files.get("image")
    if not upload or not upload.filename:
        flash("Choose a JPG or PNG image first.", "error")
        return redirect(url_for("index"))
    raw = np.frombuffer(upload.read(), np.uint8)
    frame = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if frame is None:
        flash("Unable to read this image. Try JPG or PNG.", "error")
        return redirect(url_for("index"))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    brightness = float(np.mean(gray))
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # Illustrative image-quality score only; it is NOT a measure of attention.
    score = int(max(0, min(100,
        min(len(faces) / 3, 1) * 55 +
        min(sharpness / 250, 1) * 25 +
        max(0, 20 - abs(brightness - 125) / 6.25))))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (40, 190, 90), 2)
    cv2.putText(frame, f"Faces: {len(faces)} | Demo image score: {score}",
        (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 90, 230), 2)
    ok, buffer = cv2.imencode(".jpg", frame)
    preview = base64.b64encode(buffer.tobytes()).decode("ascii") if ok else ""
    return render_template("analysis.html", faces=len(faces), score=score,
                           label=label_for(score), preview=preview)

@app.route("/export")
def export():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(get_records())
    return Response(output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"})

if __name__ == "__main__":
    app.run(debug=True)
