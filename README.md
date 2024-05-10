# Markr App

Markr is a Flask-based application for managing test results.

## Features

- Import test results from XML files
- Aggregate test results for analysis
- XML data validation for both partial and missing data
- User warnings provided in case of broken or incomplete data
- Identification and management of duplicate records during data import

## Testing
The script includes unit tests to verify the functionality of individual functions. Run the tests using:
```
python test_routes.py
```
Make sure to update the test file paths and database connection parameters as needed.


## Getting Started

### Prerequisites

- Docker installed on your system ([Docker installation guide](https://docs.docker.com/get-docker/))
- PostgreSQL database running locally or accessible via a remote connection
- Ensure that the database server is configured to accept connections from the Docker container


### Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/your-username/markr.git
   
2. Navigate to the project directory:
    ```bash
    cd markr
3. Build the Docker images:
    ```bash
    docker-compose build

### Usage

1. Start the Docker containers:
    ```bash
    docker-compose up
2. Access the application in your web browser at http://localhost:5000
3. Import test results from an XML file:
    ```bash
    curl -X POST -H 'Content-Type: text/xml+markr' http://localhost:5000/import -d @your_xml_file.xml
Replace your_xml_file.xml with the path to your XML file containing the test results. Ensure that the XML file follows the required format for importing.
4. Aggregate test results for analysis:
    ```bash
   curl -X GET http://localhost:5000/results/<test_id>/aggregate
Replace <test_id> with the ID of the test for which you want to aggregate results. For example, if the test ID is 9863, the command would be:
    ```bash
   curl -X GET http://localhost:5000/results/9863/aggregate
This command will return aggregated statistics such as mean, standard deviation, minimum, maximum, and percentiles of the obtained marks for the specified test

### Configuration

- Configure database connection settings in `config.py`
- Update the `docker-compose.yml` file with the appropriate database connection information:

  ```yaml
  services:
    web:
      environment:
        SQLALCHEMY_DATABASE_URI: 'postgresql://username:password@db_host/db_name'
        SQLALCHEMY_TRACK_MODIFICATIONS: 'false'
Replace username, password, db_host, and db_name with your PostgreSQL database credentials and connection details.

### Notes

- **Key Assumptions:**
  - The XML data provided follows a specific schema and structure.
  - The application assumes that the database schema aligns with the structure of the XML data.
  - Users are expected to provide valid XML data conforming to the expected schema.
  
- **Key Approaches:**
  - Structured Codebase: The script is structured using classes and functions, following Python's best practices for modularization and code organization. This ensures readability and maintainability of the codebase, making it easier to understand and extend.
  - Error Handling: Error handling mechanisms have been incorporated into the script to gracefully handle exceptions and unexpected scenarios. This helps prevent crashes and ensures robustness in handling various input conditions and database interactions, enhancing the overall reliability of the application.
  - Logging: Logging statements have been strategically placed throughout the code to capture important information, such as errors, warnings, and informational messages. This facilitates troubleshooting and monitoring of the script's execution, especially in production environments, enabling easier identification and resolution of issues.
  - Comments and Descriptive Naming: Comments have been added throughout the code to explain its functionality, improve readability, and aid in understanding complex sections. Variable and function names are descriptive, making the code easier to follow and enhancing its maintainability.
  - Performance Optimization:
       - Bulk Insertion: All records are read together, duplicates are removed, and records are inserted into the database using sessions, optimizing the insertion process for improved performance.
       - Minimized Database Transactions: Database transactions are minimized by collecting all import data and performing bulk operations, reducing overhead and improving overall performance.
  - Basic Testing: Unit tests have been included to verify the functionality of individual functions and ensure that the script behaves as expected. These tests cover critical components of the codebase and help catch bugs early in the development process.


- **Approach Using Flask Framework:**
  - The application utilizes the Flask framework for building web services.
  - Flask provides a lightweight and flexible environment for developing RESTful APIs.
  - Flask extensions such as Flask-SQLAlchemy and Flask-Migrate are employed for database interactions and migration management.

- **Need for a Production Server (WSGI):**
  - A production server such as a WSGI server (e.g., Gunicorn, uWSGI) is essential for deploying Flask applications in production environments.
  - WSGI servers handle incoming requests efficiently, manage concurrency, and ensure application stability and performance.
  - Using a WSGI server enables seamless scaling and deployment of Flask applications to handle production-level traffic.

- **Production Readiness:** 
    - To enhance performance and scalability, the application should employ various optimization techniques, including database indexing, query optimization, caching, and asynchronous processing.
    - Load balancing and horizontal scaling are implemented to distribute incoming traffic across multiple server instances and ensure high availability.
    - Robust error monitoring and logging mechanisms are in place to quickly identify and address issues in production, ensuring smooth operation.
    - Security measures such as authentication, authorization, and HTTPS are implemented to protect sensitive data and prevent security breaches.
    - Continuous integration and continuous deployment (CI/CD) pipelines are set up to automate testing, building, and deployment processes, facilitating faster delivery of updates to production.
    - Ensure that your application can handle concurrent access to the database efficiently, especially under high load conditions. Implement strategies such as connection pooling, transaction isolation, and database locking to maintain data consistency and prevent concurrency issues.
    - While the script optimizes performance and ensures efficient processing of large datasets, it's crucial to note that it currently lacks robust mechanisms for handling data loss. In a production environment, it's recommended to implement strategies for data redundancy, backup, and recovery to mitigate the risk of data loss in case of failures or errors during processing.
    - While the provided tests cover basic functionality, there is scope for adding more tests to ensure comprehensive test coverage. Examples of additional tests could include edge cases, handling of invalid input, and testing different scenarios to validate the robustness and reliability of the script under various conditions.

    

    
    