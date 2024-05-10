import os
import logging
from flask import Flask

# Create a logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

app = Flask(__name__)

# Configure Flask logger
app.logger.setLevel(logging.INFO)  # Set log level
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Log format

# Log to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
app.logger.addHandler(stream_handler)

# Log to file
file_handler = logging.FileHandler(os.path.join(log_dir, 'flask_app.log'))
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

app.logger.info('Flask application started')
