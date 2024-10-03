import argparse
import logging
import urllib.request
import pypdf
from pypdf import PdfReader
import tempfile
import re
import sqlite3
import os

# Initializing the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetchincidents(url):
    """
    Retrieving a PDF document from the provided URL and saving it temporarily.

    :param url: The URL of the incident PDF file.
    :return: The file path of the saved temporary PDF.
    """
    # Defining headers to mimic a browser request
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }

    # Opening the URL connection and reading the content
    pdf_request = urllib.request.Request(url, headers=request_headers)
    pdf_response = urllib.request.urlopen(pdf_request)
    pdf_content = pdf_response.read()

    # Generating a temporary file to hold the PDF
    temp_file_path = tempfile.mkstemp(suffix=".pdf")[1]
    
    # Opening the temporary file and writing the PDF content
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(pdf_content)

    return temp_file_path

def extractincidents(pdf_file_path):
    """
    Extract incident data from the provided PDF and return a list of tuples.
    
    :param pdf_file_path: Path to the PDF file.
    :return: List of tuples containing the extracted incident data.
    """
    def is_complete_row(fields):
        """Check if the row contains exactly 5 fields."""
        return len(fields) == 5

    def clean_and_split(line):
        """Clean and split each line by spaces, removing extra whitespaces."""
        return re.split(r"\s{2,}", line.strip())

    incidents_list = []
    
    # Reading the PDF
    reader = PdfReader(pdf_file_path)
    first_page = True
    
    # Iterating through each page in the PDF
    for page in reader.pages:
        # Extracting page text and splitting it into lines
        raw_text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)
        lines = raw_text.split("\n")
        
        # Skipping the header processing if it's the first page
        if first_page:
            first_page = False
            lines = lines[3:] 
        
        # Processing each line on the page
        for line in lines:
            fields = clean_and_split(line)
            if is_complete_row(fields):
                # Add the tuple containing incident fields to the list
                incidents_list.append(tuple(fields))
    
    return incidents_list  # Returning a list of tuples

def createdb():
    """
    Creating a SQLite database file 'normanpd.db' in the 'resources' directory.
    If the file already exists, it will be deleted and a new one will be created.
    """
    # Defining the path for the database in the 'resources' directory
    db_path = os.path.join('resources', 'normanpd.db')
    
    # Removing existing database file if it exists
    if os.path.isfile(db_path):
        os.unlink(db_path)  # Deleting the file safely
        print(f"Existing database has been removed: {db_path}")
    
    # Establishing a new connection to the database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Creating the 'incidents' table within the database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            incident_time TEXT,
            incident_number TEXT,
            incident_location TEXT,
            nature TEXT,
            incident_ori TEXT
        )
    ''')
    connection.commit()
    print(f"New database and table have been created at: {db_path}")
    
    return connection

def populatedb(db, incidents):
    """
    Populating the SQLite database with incident data using tuples.
    
    :param db: Connection to the SQLite database.
    :param incidents: List of tuples with incident data.
    """
    cursor = db.cursor()
    
    # Inserting incident data into the database
    cursor.executemany('''
        INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori)
        VALUES (?, ?, ?, ?, ?)
    ''', incidents)  # Each tuple in the list is passed to the query

    db.commit()

def status(db):
    """
    Printing the count of each nature of incidents.
    """
    cursor = db.cursor()
    cursor.execute('SELECT nature, COUNT(*) FROM incidents GROUP BY nature order by nature ASC')
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}|{row[1]}")

def main(url):
    # Downloading data
    incident_data = fetchincidents(url)

    # Extracting data
    incidents = extractincidents(incident_data)
	
    # Creating new database
    db = createdb()
	
    # Inserting data
    populatedb(db, incidents)
	
    # Printing incident counts
    status(db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="Incident summary URL.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
