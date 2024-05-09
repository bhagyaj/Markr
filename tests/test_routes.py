from unittest.mock import patch
from flask import Response
from app.routes import validate_xml
from lxml.etree import XMLSyntaxError
from app.routes import import_results, TestResults
import unittest
from app import create_app, db

class TestRoutes(unittest.TestCase):

    def test_valid_xml(self):
        # Read the contents of the XML file
        with open('sample_results.xml', 'rb') as f:
            xml_content = f.read()

        # Call the validate_xml method
        result, _ = validate_xml(xml_content)

        # Assert the result
        self.assertTrue(result)

    def test_invalid_xml(self):
        # Pass invalid XML content (empty content)
        invalid_xml_content = b''

        # Call the validate_xml method with invalid XML content
        result, _ = validate_xml(invalid_xml_content)

        # Assert the result
        self.assertFalse(result)

    def test_missing_fields(self):
        # Create XML content with missing fields
        xml_content = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <mcq-test-results>
            <mcq-test-result scanned-on="2017-01-01T00:00:00Z">
                <first-name>Jimmmy</first-name>
                <last-name>Student</last-name>
                <!-- Missing student-number and test-id -->
                <summary-marks available="10" obtained="2" />
            </mcq-test-result>
        </mcq-test-results>"""

        # Call the validate_xml method with XML content with missing fields
        result, errors = validate_xml(xml_content)

        # Assert that the result is False, indicating missing fields
        self.assertFalse(result)

        # Assert that the error contains the expected message
        self.assertIn({'error': 'Missing fields: student-number, test-id'}, errors)

    def test_missing_values(self):
        # Create XML content with missing values for some fields
        xml_content = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <mcq-test-results>
            <mcq-test-result scanned-on="2017-01-01T00:00:00Z">
                <!-- Empty first-name and test-id -->
                <first-name></first-name>
                <last-name>Student</last-name>
                <student-number>99999999</student-number>
                <test-id></test-id>
                <summary-marks available="10" obtained="2" />
            </mcq-test-result>
        </mcq-test-results>"""

        # Call the validate_xml method with XML content with missing values
        result, errors = validate_xml(xml_content)

        # Assert that the result is False, indicating missing values
        self.assertFalse(result)

        # Assert that the error contains the expected message
        self.assertIn({'error': 'Missing values for fields: first-name, test-id'}, errors)

    def setUp(self):
        # Create a Flask application for testing
        self.app = create_app()
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_import_results(self):
        # Define the sample XML data
        sample_xml = """<?xml version="1.0" encoding="UTF-8" ?>
        <mcq-test-results>
            <mcq-test-result scanned-on="2017-12-04T13:47:10+11:00">
                <first-name>Bob</first-name>
                <last-name>Bob</last-name>
                <student-number>2394</student-number>
                <test-id>9863</test-id>
                <summary-marks available="20" obtained="17" />
            </mcq-test-result>
        </mcq-test-results>"""

        # Convert the sample XML string to bytes
        sample_xml_bytes = sample_xml.encode('utf-8')

        # Mock the request context and data
        with self.app.test_request_context('/', data=sample_xml_bytes, content_type='text/xml+markr'):
            # Call the import_results function within the application context
            response = import_results()

        # Assert that the response indicates successful import
        self.assertEqual(response, ('Results imported successfully', 200))

        # Retrieve the imported record from the database
        with self.app.app_context():
            imported_record = TestResults.query.filter_by(student_number='2394', test_id='9863').first()

            # Assert that the record was imported correctly
            self.assertIsNotNone(imported_record)
            self.assertEqual(imported_record.first_name, 'Bob')
            self.assertEqual(imported_record.last_name, 'Bob')
            self.assertEqual(imported_record.available_marks, 20)
            self.assertEqual(imported_record.obtained_marks, 17)