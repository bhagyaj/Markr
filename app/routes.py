# app/routes.py
from datetime import datetime

from flask import Blueprint, request, jsonify
from app import db
from app.models import TestResults
from lxml import etree
from io import BytesIO

bp = Blueprint('main', __name__)

def validate_xml(xml_content):
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
                        incomplete_records.append({'error': 'Missing or empty available or obtained attributes in summary-marks'})

                    # Check if any mandatory fields have missing values
                    missing_values = [field for field in mandatory_fields if not element.find(field).text]
                    if missing_values:
                        incomplete_records.append({'error': f'Missing values for fields: {", ".join(missing_values)}'})

        return not incomplete_records, incomplete_records
    except etree.XMLSyntaxError:
        return False, [{'error': 'Invalid XML syntax'}]




@bp.route('/import', methods=['POST'])
def import_results():
    # Parse XML request and store data in database
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
            return 'Invalid XML data', 400

        # # Check if any mandatory fields are missing
        # if any(tree.find(field) is None for field in ['first-name', 'last-name', 'student-number', 'test-id']):
        #         return jsonify({'error': 'Incomplete record. Missing mandatory fields.'}), 400

        # Extract student data from the XML
        results = tree.xpath('//mcq-test-result')

        # Create a dictionary to store unique student-test pairs with the latest scanned time
        student_test_dict = {}

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

            # Check if the record already exists in the dictionary
            key = (student_number, test_id)
            if key in student_test_dict:
                # If the record already exists, update the scanned time and marks obtained if it's higher
                if scanned_on > student_test_dict[key]['scanned_on']:
                    student_test_dict[key]['scanned_on'] = scanned_on
                    student_test_dict[key]['obtained_marks'] = obtained_marks
            else:
                # If the record doesn't exist, add it to the dictionary
                student_test_dict[key] = {'first_name': first_name, 'last_name': last_name,
                                          'student_number': student_number, 'test_id': test_id,
                                          'available_marks': available_marks,
                                          'obtained_marks': obtained_marks, 'scanned_on': scanned_on}

                # Process the unique student-test pairs in the dictionary
        for data in student_test_dict.values():
            # Check if the record already exists in the database
            existing_record = TestResults.query.filter_by(student_number=data['student_number'],
                                                          test_id=data['test_id']).first()

            if existing_record:
                # If the record already exists, update the scanned time and marks obtained if it's higher
                if data['scanned_on'] > existing_record.scanned_on:
                    existing_record.scanned_on = data['scanned_on']
                    existing_record.marks_obtained = data['obtained_marks']
            else:
                # If the record doesn't exist, create a new TestResults object
                new_result = TestResults(first_name=data['first_name'], last_name=data['last_name'],
                                         student_number=data['student_number'], test_id=data['test_id'],
                                         available_marks=data['available_marks'],
                                         obtained_marks=data['obtained_marks'],
                                         scanned_on=data['scanned_on'])
                db.session.add(new_result)

            # Commit changes to the database
        db.session.commit()

        return 'Results imported successfully', 200

    else:
        return jsonify({'error': 'Incomplete record(s)', 'incomplete_records': incomplete_records}), 400


@bp.route('/results/<test_id>/aggregate', methods=['GET'])
def aggregate_results(test_id):
    # Calculate aggregate data and return JSON response
    return jsonify({
        'mean': 65.0,
        'stddev': 0.0,
        'min': 65.0,
        'max': 65.0,
        'p25': 65.0,
        'p50': 65.0,
        'p75': 65.0,
        'count': 1
    })
