import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Result
from detector import detect_threat
from werkzeug.utils import secure_filename

import email
from email import policy
from email.parser import BytesParser
from docx import Document
import PyPDF2

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
with app.app_context():
    db.create_all()

# --- TEXT EXTRACTION ---
def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    try:
        if ext in [".txt", ".log"]:
            with open(filepath, "r", errors="ignore") as f:
                text = f.read()
        elif ext == ".eml":
            with open(filepath, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)
                sender = msg.get('From')
                subject = msg.get('Subject')
                date = msg.get('Date')
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body = msg.get_body(preferencelist=('plain')).get_content()
                text = f"Sender: {sender}\nDate: {date}\nSubject: {subject}\n\n{body}"
        elif ext == ".docx":
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == ".pdf":
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        else:
            text = "Unsupported file type."
    except Exception as e:
        text = f"Error extracting text: {str(e)}"
    return text

# --- UTILS ---
def clean_text(text):
    # Keep some structure but remove excess whitespace and URLs for the AI model
    text = re.sub(r'\n+', '\n', text)
    # Note: We don't remove URLs here anymore because the detector needs to count them for DoS
    return text.strip()

def generate_summary(text):
    sentences = text.split('.')
    return '.'.join(sentences[:2]) if len(sentences) > 1 else text

# --- ROUTES ---

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # 1. Technical Processing
    raw_content = extract_text(filepath)
    cleaned_content = clean_text(raw_content)

    # 2. Detailed Detection
    # Ensure your detector.py returns a dictionary with: 
    # status, severity, confidence, reason, and findings
    result = detect_threat(cleaned_content)

    # 3. Dynamic Summary
    summary = generate_summary(cleaned_content)

    # 4. Save to Database
    new_record = Result(
        filename=file.filename,
        threat=(result["status"] != "SECURE"),
        severity=result["severity"]
    )
    db.session.add(new_record)
    db.session.commit()

    # 5. Return Detailed Data for Frontend
    return jsonify({
        "status": result["status"],        # e.g., "THREAT", "SPAM", "SECURE"
        "severity": result["severity"],    # e.g., "HIGH", "MEDIUM", "LOW"
        "confidence": result.get("confidence", 0), # New: For progress bars
        "reason": result.get("reason", ""),        # New: To show the user "Why"
        "findings": result.get("findings", []),   # New: List of STRIDE matches
        "summary": summary
    })

@app.route("/api/results", methods=["GET"])
def get_results():
    all_data = Result.query.all()
    return jsonify([{
        "filename": r.filename,
        "threat": r.threat,
        "severity": r.severity
    } for r in all_data])

@app.route("/api/clear", methods=["POST"])
def clear_history():
    try:
        Result.query.delete()
        db.session.commit()
        return jsonify({"message": "History cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)