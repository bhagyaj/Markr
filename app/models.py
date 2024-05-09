
from app import db

class TestResults(db.Model):
    student_number = db.Column(db.String(20), primary_key=True)
    test_id = db.Column(db.String(20), primary_key=True)
    scanned_on = db.Column(db.DateTime)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    available_marks = db.Column(db.Integer)
    obtained_marks = db.Column(db.Integer)
