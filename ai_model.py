from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# -------------------------------
# TRAINING DATA (SIMPLE)
# -------------------------------
emails = [

    # ---------------- SPAM (1) ----------------
    "win free prize now",
    "click here to buy now",
    "limited time offer free",
    "congratulations you won lottery",
    "claim your prize now",
    "urgent offer click here",
    "buy now huge discount",
    "get free money instantly",
    "exclusive deal limited offer",
    "win cash prize today",
    "earn money fast online",
    "cheap products buy now",
    "special discount just for you",
    "act now limited deal",
    "click here to claim reward",
    "free gift card available",
    "double your income fast",
    "limited offer hurry up",
    "best deal of the day",
    "win big rewards now",

    # ---------------- WORK / NORMAL (0) ----------------
    "meeting tomorrow project discussion",
    "deadline for submission",
    "team meeting schedule",
    "project update and report",
    "please review the document",
    "let us discuss in meeting",
    "schedule a call with client",
    "project deadline extended",
    "status update required",
    "team collaboration meeting",
    "client meeting tomorrow",
    "report submission due date",
    "weekly project review meeting",
    "update the project status",
    "discussion on project progress",
    "schedule meeting with manager",
    "team needs to complete task",
    "deadline approaching submit work",
    "review the code changes",
    "prepare report for meeting"
]

labels = [1]*20 + [0]*20
# -------------------------------
# TRAIN MODEL
# -------------------------------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(emails)

model = MultinomialNB()
model.fit(X, labels)

# -------------------------------
# PREDICTION FUNCTION
# -------------------------------
def predict_spam(text):
    X_test = vectorizer.transform([text])
    prediction = model.predict(X_test)[0]
    probability = model.predict_proba(X_test)[0][prediction]

    return prediction, round(probability * 100, 2)