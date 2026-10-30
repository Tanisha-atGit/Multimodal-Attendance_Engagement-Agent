# ClassPulse — Multimodal Attendance & Engagement Agent

A beginner-friendly local Flask prototype for an educational project.

## Features
- Attendance records with student name, ID, session, timestamp, and status.
- Manual demo score categories (High / Moderate / Low).
- OpenCV-based face detection on a user-selected classroom/test image.
- Image clarity and lighting indicators.
- Create classroom sessions.
- Download attendance data as CSV.
- Local CSV/JSON storage. Uploaded analysis images are processed in memory and not saved.

## Responsible use / limitations
This is a demonstration prototype, not a production attendance or engagement measurement system. The image score is a simple heuristic based on face visibility, sharpness, and brightness; it does **not** measure real attention, emotion, or learning. Face detection can miss people or detect incorrectly. Do not use this score to grade or penalize students. Use consented/test images and explain the privacy implications before any real deployment.

## Run on Windows using VS Code
1. Extract the ZIP and open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
4. Activate it:
   ```powershell
   .venv\Scripts\activate
   ```
5. Install packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```
6. Run:
   ```powershell
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your browser.

Internet is needed to install dependencies. The app itself runs locally after installation.

## Suggested demo flow
1. Add two sample student records.
2. Create a session.
3. Upload a test/consented image to demonstrate face detection.
4. Download the CSV report.
5. Explain the prototype's limitations in your presentation.
