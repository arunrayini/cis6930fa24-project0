import argparse
import logging
import pandas as pd
import urllib.request
import pypdf
from pypdf import PdfReader
import tempfile
import re
import sqlite3
import os

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetchincidents(url):
    """
    Downloads the incident PDF from the provided URL and saves it to a temporary file.
    
    :param url: URL of the incident PDF file
    :return: Path to the saved PDF file
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    
    # Read the content of the PDF
    pdf_content = response.read()
    
    # Write the PDF content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_content)
        temp_pdf_path = temp_pdf.name
    
    return temp_pdf_path

def extractincidents(pdf_file_path):
    # Initialize necessary variables
    first_page_flag = True
    field_count = 3
    data_store = []
    
    # Read the PDF file
    read_file = PdfReader(pdf_file_path)

    for page in read_file.pages:
        page_text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False).split("\n")

        if first_page_flag:
            # Process headers only on the first page
            headers = re.split(r"\s{2,}", page_text[2])[1:]
            first_page_flag = False
            # Skip the header lines
            page_text = page_text[3:]

        # Add valid rows (those with 5 fields) to the data_store
        for line in page_text:
            row_data = re.split(r"\s{2,}", line.strip())
            if len(row_data) == 5:
                data_store.append([field.strip() for field in row_data])

    # Filter valid rows based on field count
    data_store = [row for row in data_store if len(row) >= field_count and any(row)]

    # Convert the list to a DataFrame
    incidents_df = pd.DataFrame(data_store, columns=['incident_time', 'incident_number', 'incident_location', 'nature', 'incident_ori'])
    return incidents_df

def createdb():
    """
    Create a SQLite database named 'normanpd.db' in the 'resources' directory. 
    If it already exists, it will be overwritten.
    """
    # Define the path to the database in the 'resources' directory
    db_path = os.path.join('resources', 'normanpd.db')
    
    # Check if the database already exists and delete it
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database: {db_path}")

    # Create a new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the 'incidents' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            incident_time TEXT,
            incident_number TEXT,
            incident_location TEXT,
            nature TEXT,
            incident_ori TEXT
        )
    ''')
    conn.commit()
    print(f"Created new database and table at {db_path}.")
    
    return conn

def populatedb(db, incidents):
    """
    Populate the SQLite database with incident data.
    
    :param db: Connection to the SQLite database.
    :param incidents: List of incident data to be inserted.
    """
    cursor = db.cursor()
    
    # Insert incident data into the database
    cursor.executemany('''
        INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori)
        VALUES (:incident_time, :incident_number, :incident_location, :nature, :incident_ori)
    ''', incidents.to_dict('records'))  # Convert the DataFrame rows to dictionary format
    
    db.commit()
    # print(f"Inserted {len(incidents)} records into the database.")

def status(db):
    """
    Print the count of each nature of incidents.
    """
    cursor = db.cursor()
    cursor.execute('SELECT nature, COUNT(*) FROM incidents GROUP BY nature order by nature ASC')
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}|{row[1]}")

def main(url):
    # Download data
    incident_data = fetchincidents(url)

    # Extract data
    incidents = extractincidents(incident_data)
	
    # Create new database
    db = createdb()
	
    # Insert data
    populatedb(db, incidents)
	
    # Print incident counts
    status(db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
