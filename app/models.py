import logging
from app import db
from sqlalchemy.exc import SQLAlchemyError

# Create a logger instance
logger = logging.getLogger(__name__)

class TestResults(db.Model):
    """
       Model class for storing test results in the database.

       Attributes:
           student_number (str): The student's unique identification number.
           test_id (str): The unique identifier for the test.
           scanned_on (datetime): The date and time when the test was scanned.
           first_name (str): The first name of the student.
           last_name (str): The last name of the student.
           available_marks (int): Total marks available for the test.
           obtained_marks (int): Marks obtained by the student in the test.
       """
    student_number = db.Column(db.String(20), primary_key=True)
    test_id = db.Column(db.String(20), primary_key=True)
    scanned_on = db.Column(db.DateTime)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    available_marks = db.Column(db.Integer)
    obtained_marks = db.Column(db.Integer)
