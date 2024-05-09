FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add commands for database migration
# RUN flask db init
# RUN flask db migrate -m "Initial migration"
# RUN flask db upgrade

CMD ["flask", "run", "--host=0.0.0.0"]
