# Use the official Python 3.8 image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file from the local directory to the container's working directory
COPY requirements.txt .

# Install the Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire local directory into the container's working directory
COPY . .

# Database migration commands (uncomment and modify as needed)
# RUN flask db init
# RUN flask db migrate -m "Initial migration"

# Apply any database migrations
RUN flask db upgrade

# Command to start the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
