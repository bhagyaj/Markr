from datetime import datetime
from unittest.mock import patch
from flask import Response
from app.routes import validate_xml
from lxml.etree import XMLSyntaxError
from app.routes import import_results, TestResults, aggregate_results
import unittest
from app import create_app, db
import numpy as np
import json

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


    def test_aggregate_results(self):
        # Define test data
        test_id = '123'
        obtained_marks_list = [65, 70, 75, 80, 85]

        # Create sample records in the database
        with self.app.test_request_context():
            for i, obtained_mark in enumerate(obtained_marks_list, start=1):
                new_result = TestResults(first_name='Sample', last_name='Student',
                                         student_number=f'1234{i}',  # Use unique student numbers
                                         test_id=test_id,
                                         available_marks=100, obtained_marks=obtained_mark,
                                         scanned_on=datetime.now())
                db.session.add(new_result)
            db.session.commit()

            # Call the aggregate_results method
            response = aggregate_results(test_id)

        # Expected results
        mean = np.mean(obtained_marks_list)
        stddev = np.std(obtained_marks_list)
        min_value = np.min(obtained_marks_list)
        max_value = np.max(obtained_marks_list)
        p25, p50, p75 = np.percentile(obtained_marks_list, [25, 50, 75])
        p25_percentage = p25 * 100 / 100  # Assuming available marks is 100
        p50_percentage = p50 * 100 / 100
        p75_percentage = p75 * 100 / 100

        expected_response = {
            'mean': mean,
            'stddev': stddev,
            'min': min_value,
            'max': max_value,
            'p25': p25_percentage,
            'p50': p50_percentage,
            'p75': p75_percentage,
            'count': len(obtained_marks_list)
        }

        # Decode bytes to string and parse as JSON
        response_data = json.loads(response[0].data.decode('utf-8'))

        # Convert response to JSON and compare with expected response
        self.assertEqual(response_data, expected_response)
        self.assertEqual(response[1], 200)


