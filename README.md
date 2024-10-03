# cis6930fa24 -- Project 0

Name: Arun Kumar Reddy Rayini

# Project Description:
This project is aimed at retrieving incident report data from a PDF file provided through a URL. The program extracts key details, organizes the data into tuples, and stores it in a SQLite database. It then analyzes the data and presents the counts of various incident types for further review. The PDF contains a daily incident summary, and the code handles processing and structuring this information for better analysis.

# Development Process
Step 1: Fetching the PDF
The fetchincidents() function is responsible for downloading the PDF file from the given URL and saving it temporarily for further processing.

Step 2: Extracting Incident Data
The extractincidents() function processes the downloaded PDF file, extracts key information such as time, incident number, location, type (nature), and ORI, and returns the data as a list of tuples.

Step 3: Database Creation
The createdb() function creates a fresh SQLite database and sets up the required table schema. It deletes any existing database of the same name to ensure a fresh start every time the program runs.

Step 4: Populating the Database
Once the incident data is extracted from the PDF, the populatedb() function inserts the data into the SQLite database as rows in the incidents table.

Step 5: Displaying a Summary
Finally, the status() function queries the database to count how many times each type of incident occurs and displays the results.

# How to install
1.Install dependencies using pipenv: pipenv install

2.Activate the pipenv environment: pipenv shell

# How to Run
To fetch incidents, store them in a database, and display the incident type counts, use the following command:  pipenv run python project0/main.py --incidents "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"

For testing: pipenv run python -m pytest -v  

# Demo

# Functions

fetchincidents(url)
Description: Downloads the PDF from the provided URL and saves it in a temporary file.
Returns: Path to the saved temporary file.

extractincidents(pdf_file_path)
Description: Extracts incident data (time, number, location, nature, ORI) from the PDF file and stores it in a list of tuples.
Returns: List of tuples containing the extracted incident data.

createdb()
Description: Creates an SQLite database file in the 'resources' directory. If the database file already exists, it is deleted, and a new one is created.
Returns: SQLite connection object.

populatedb(db, incidents)
Description: Inserts the extracted incident data into the SQLite database.
Parameters:
db (SQLite connection object) - The connection to the database.
incidents (list of tuples) - The extracted incident data.

status(db)
Description: Displays the count of each type of incident from the database.
Parameters: db (SQLite connection object) - The connection to the database.

# Database Development

The goal of the database in this project is to store the extracted incident data from the PDF file in a structured format. The SQLite database was chosen for its simplicity and lightweight nature, which makes it ideal for small to medium-sized applications.

Table Design
The SQLite database contains a single table named incidents. This table is designed to hold all relevant information about each reported incident. The schema for this table is as follows:

incident_time (TEXT): This field stores the date and time of the incident as recorded in the PDF. It allows us to know when each event took place.

incident_number (TEXT): This is a unique identifier assigned to each incident. It is typically a combination of the year and a sequential number, ensuring that each incident can be referenced individually.

incident_location (TEXT): This field captures the location where the incident occurred. The format is usually a street address or a general location within the city, helping to geographically identify the area involved in the incident.

nature (TEXT): The nature of the incident describes the type of event that occurred. Examples include "Traffic Stop", "Welfare Check", and other categories that provide context about the situation.

incident_ori (TEXT): ORI stands for "Originating Agency Identifier," a code assigned to law enforcement agencies. This field stores the ORI code, which is useful in identifying the agency that handled the incident.

# Database Workflow

Database Creation:

The createdb() function is responsible for creating the SQLite database. The database file is named normanpd.db and is stored in the resources directory.
Before creating a new database, the function checks if a database with the same name already exists. If so, the old database is deleted to ensure that each run starts with a fresh database.
After ensuring the old database is removed (if applicable), a new database connection is established, and the schema for the incidents table is created.
The table schema ensures that the database is ready to accept and store the incident data extracted from the PDF.

Populating the Database:

Once the PDF has been processed and the incident data has been extracted, the next step is inserting this data into the database.
The populatedb() function handles this task. It takes the list of tuples generated from the extractincidents() function and inserts each tuple as a row in the incidents table.
The function uses the cursor.executemany() method, which allows multiple rows to be inserted efficiently in one query. Each tuple contains five values corresponding to the five columns in the table (incident_time, incident_number, incident_location, nature, incident_ori).

Querying the Database:

After the data has been inserted into the database, we can perform queries to extract insights from the data.
The status() function runs a query that groups the incidents by their nature (type of incident) and counts how many incidents occurred for each type. This provides a useful summary of the different types of incidents recorded in the PDF.
The query is executed using the SQL GROUP BY clause, which aggregates the results by the nature column, and the COUNT() function calculates the total for each incident type.

# Testing

Testing was a crucial part of this project, and we ensured each function had test coverage.

# Tests Implemented

test_fetchincidents()
Objective: Ensuring the fetchincidents() function correctly fetches the PDF content and stores it in a temporary file.
Strategy: We used the mock_open() and patch() functions to simulate downloading the PDF file without making an actual network request.

test_populatedb()
Objective: Verifying that the populatedb() function inserts the data correctly into the SQLite database.
Strategy: We inserted mock incident data into a temporary SQLite database and checked whether the records were inserted correctly.

test_status()
Objective: Verifying that the status() function accurately prints the count of each incident type.
Strategy: We captured the output of the status() function and compared it with the expected result to ensure correctness.

# Bugs and Assumptions

Known Bugs:
The extraction logic assumes the PDF structure will remain consistent. If the structure changes, the data extraction might break.
The extraction could be slow if the PDF is large or contains many pages.

Assumptions:
The incident data in the PDF will always contain exactly five fields (time, number, location, nature, ORI).
The format of the incident summary PDF will not change significantly.
The list of tuples extracted from the PDF will match the structure of the SQLite database.






 
