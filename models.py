from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    threat = db.Column(db.Boolean)
    severity = db.Column(db.String(20))