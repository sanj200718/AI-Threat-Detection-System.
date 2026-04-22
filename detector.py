import re
from ai_model import predict_spam

# Added more specific patterns to close "loopholes"
STRIDE_PATTERNS = {
    "Spoofing": [r"from:.*@(gmail|yahoo)\.com", r"reply-to:", r"sender: unknown"],
    "Tampering": [r"<script>", r"javascript:", r"eval\(", r"onerror="],
    "Information Disclosure": [r"password", r"ssn", r"credit card", r"api_key", r"private_key"],
    "Elevation of Privilege": [r"admin access", r"root access", r"sudo ", r"chmod 777"]
}

def detect_threat(file_content):
    text = file_content.lower()
    
    # Initialize response data
    results = {
        "status": "SECURE",
        "severity": "NONE",
        "category": "PERSONAL",
        "confidence": 0,
        "reason": "No suspicious patterns detected.",
        "findings": []
    }

    # 1. Check High-Severity Signatures (SQLi / XSS)
    high_threats = ["select * from", "drop table", "union select", "<script>"]
    for word in high_threats:
        if word in text:
            results.update({
                "status": "THREAT",
                "severity": "HIGH",
                "category": "SIGNATURE",
                "confidence": 98,
                "reason": f"Malicious signature detected: {word}"
            })
            return results

    # 2. STRIDE Pattern Matching
    for stride_type, patterns in STRIDE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                results["findings"].append(stride_type)
    
    # 3. Denial of Service (DoS) Logic
    links = re.findall(r'http\S+', text)
    if len(links) > 3:
        results["findings"].append("Denial of Service")

    # 4. AI Spam Prediction
    ai_prediction, ai_confidence = predict_spam(text)

    # FINAL DECISION LOGIC (Dynamic weighting)
    if results["findings"]:
        results.update({
            "status": "THREAT",
            "severity": "MEDIUM",
            "category": "STRIDE",
            "confidence": 85,
            "reason": f"Matches found for: {', '.join(set(results['findings']))}"
        })
    elif ai_prediction == 1:
        results.update({
            "status": "SPAM",
            "severity": "LOW",
            "category": "AI_CLASSIFIER",
            "confidence": round(ai_confidence * 100, 2),
            "reason": "AI model identified suspicious promotional patterns."
        })
    elif any(word in text for word in ["meeting", "project", "deadline", "team"]):
        results.update({
            "status": "SECURE",
            "category": "WORK",
            "confidence": 90,
            "reason": "Validated as professional correspondence."
        })

    return results