
from app import db

class TestResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scanned_on = db.Column(db.DateTime)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    student_number = db.Column(db.String(20))
    test_id = db.Column(db.String(20))
    available_marks = db.Column(db.Integer)
    obtained_marks = db.Column(db.Integer)
