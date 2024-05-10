# app/routes.py
from datetime import datetime
import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models import TestResults
from lxml import etree
from io import BytesIO
import numpy as np

bp = Blueprint('main', __name__)

# Create a logger instance
logger = logging.getLogger(__name__)


def validate_xml(xml_content):
    """
        Validate the XML content to ensure it meets the required format.

        Args:
            xml_content (bytes): The XML content to validate.

        Returns:
            bool: True if the XML is valid, False otherwise.
            list: A list of incomplete records if any.
        """
    try:
        root = etree.parse(BytesIO(xml_content))
        incomplete_records = []

        # Check if there are any mcq-test-result elements
        test_results = root.findall('.//mcq-test-result')
        if not test_results:
            return False, [{'error': 'No mcq-test-result elements found'}]

        # Define a list of mandatory fields
        mandatory_fields = ['first-name', 'last-name', 'student-number', 'test-id']

        # Check if all mandatory fields are present in each mcq-test-result element
        for element in test_results:
            missing_fields = [field for field in mandatory_fields if element.find(field) is None]
            if missing_fields:
                incomplete_records.append({'error': f'Missing fields: {", ".join(missing_fields)}'})
            else:
                # Check if the summary-marks element exists
                summary_marks = element.find('summary-marks')
                if summary_marks is None:
                    incomplete_records.append({'error': 'Missing summary-marks element'})
                else:
                    # Check if available and obtained attributes exist and have values
                    available = summary_marks.get('available')
                    obtained = summary_marks.get('obtained')
                    if not available or not obtained:
                        incomplete_records.append(
                            {'error': 'Missing or empty available or obtained attributes in summary-marks'})

                    # Check if any mandatory fields have missing values
                    missing_values = [field for field in mandatory_fields if not element.find(field).text]
                    if missing_values:
                        incomplete_records.append({'error': f'Missing values for fields: {", ".join(missing_values)}'})

        return not incomplete_records, incomplete_records
    except etree.XMLSyntaxError:
        logger.error("Invalid XML syntax")
        return False, [{'error': 'Invalid XML syntax'}]


@bp.route('/import', methods=['POST'])
def import_results():
    """
        Import test results from XML data into the database.
        """

    # Check if the request contains XML data
    if request.content_type != 'text/xml+markr':
        return 'Unsupported Media Type', 415

    # Get the XML data from the request
    xml_data = request.data

    is_valid, incomplete_records = validate_xml(xml_data)

    if is_valid:

        # Parse the XML data
        try:
            tree = etree.parse(BytesIO(xml_data))
        except etree.XMLSyntaxError:
            logger.error("Invalid XML data")
            return 'Invalid XML data', 400

        # Extract student data from the XML
        results = tree.xpath('//mcq-test-result')

        for result in results:
            first_name = result.find('first-name').text
            last_name = result.find('last-name').text
            student_number = result.find('student-number').text
            test_id = result.find('test-id').text
            available_marks = int(result.find('summary-marks').get('available'))
            obtained_marks = int(result.find('summary-marks').get('obtained'))

            # Extract and parse the scanned-on attribute
            scanned_on_str = result.get('scanned-on')
            scanned_on = datetime.strptime(scanned_on_str, '%Y-%m-%dT%H:%M:%S%z')

            # Check if the record already exists in the database
            existing_record = TestResults.query.filter_by(student_number=student_number, test_id=test_id).first()

            if existing_record:
                # If the record already exists, update it
                existing_record.scanned_on = scanned_on
                existing_record.first_name = first_name
                existing_record.last_name = last_name
                existing_record.available_marks = available_marks
                existing_record.obtained_marks = obtained_marks
            else:
                # If the record doesn't exist, create a new TestResults object
                new_result = TestResults(student_number=student_number, test_id=test_id,
                                         first_name=first_name, last_name=last_name,
                                         available_marks=available_marks, obtained_marks=obtained_marks,
                                         scanned_on=scanned_on)
                db.session.add(new_result)

            # Commit changes to the database
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing changes to the database: {e}")
            return 'Error committing changes to the database', 500

        return 'Results imported successfully', 200

    else:
        logger.error("Incomplete record(s) in XML data")
        return jsonify({'error': 'Incomplete record(s)', 'incomplete_records': incomplete_records}), 400


@bp.route('/results/<test_id>/aggregate', methods=['GET'])
def aggregate_results(test_id):
    """
       Aggregate results for a given test ID.
       """

    # Query the database to get marks obtained for the given test_id
    obtained_marks_list = [result.obtained_marks for result in TestResults.query.filter_by(test_id=test_id).all()]

    # Calculate mean
    mean = np.mean(obtained_marks_list)

    # Calculate count
    count = len(obtained_marks_list)

    # Calculate standard deviation
    stddev = np.std(obtained_marks_list)

    # Calculate minimum value
    min_value = int(np.min(obtained_marks_list))

    # Calculate maximum value
    max_value = int(np.max(obtained_marks_list))

    # Calculate percentiles
    percentiles = np.percentile(obtained_marks_list, [25, 50, 75])

    # Calculate percentiles as a percentage of available marks
    available_marks = TestResults.query.filter_by(test_id=test_id).first().available_marks
    percentiles_percentage = [p * 100 / available_marks for p in percentiles]

    # Construct the response
    response = {
        'mean': mean,
        'stddev': stddev,
        'min': min_value,
        'max': max_value,
        'p25': percentiles_percentage[0],
        'p50': percentiles_percentage[1],
        'p75': percentiles_percentage[2],
        'count': count
    }

    # Return the response as JSON
    return jsonify(response), 200
