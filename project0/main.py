import argparse
import sqlite3
import urllib.request
import fitz  # PyMuPDF
import logging
import re
import os

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetchincidents(url):
    """
    Download the incident PDF from the given URL.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    return response.read()

def extractincidents(incident_data):
    """
    Extract incidents from the PDF data.
    """
    doc = fitz.open(stream=incident_data, filetype="pdf")
    all_data = []
    
    # Iterate through each page
    for page_num in range(len(doc)):
        #logger.info(f"Processing page {page_num + 1}")
        page = doc.load_page(page_num)
        
        # Extract text from the page
        page_text = page.get_text("text")
        
        # Split lines and process
        lines = page_text.split("\n")
        
        current_incident = []
        for line in lines:
            line = line.strip()
            
            # Check if the line matches a Date/Time pattern
            if re.match(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}', line):
                if len(current_incident) == 5:
                    all_data.append({
                        'incident_time': current_incident[0],
                        'incident_number': current_incident[1],
                        'incident_location': current_incident[2],
                        'nature': current_incident[3],
                        'incident_ori': current_incident[4]
                    })
                current_incident = [line]  # Start a new incident

            # Continue capturing the remaining fields
            elif current_incident and len(current_incident) < 5:
                current_incident.append(line)
            
            # Once we have all 5 fields, capture the incident
            if len(current_incident) == 5:
                all_data.append({
                    'incident_time': current_incident[0],
                    'incident_number': current_incident[1],
                    'incident_location': current_incident[2],
                    'nature': current_incident[3],
                    'incident_ori': current_incident[4]
                })
                current_incident = []  # Reset for the next incident
    
    #logger.info(f"Extracted {len(all_data)} unique incidents from the PDF.")
    return all_data

def createdb(conn=None):
    """
    Create a SQLite database. If the database already exists, delete it and create a new one.
    """
    db_path = 'resources/normanpd.db'
    
    # Check if the database already exists and delete it
    if os.path.exists(db_path):
        os.remove(db_path)
        #logger.info(f"Deleted existing database: {db_path}")

    # Create a new database
    if conn is None:
        conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
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
    #logger.info("Created new database and table.")
    return conn

def populatedb(db, incidents):
    """
    Populate the SQLite database with incident data.
    """
    cursor = db.cursor()
    cursor.executemany('''
        INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori)
        VALUES (:incident_time, :incident_number, :incident_location, :nature, :incident_ori)
    ''', incidents)
    db.commit()

def status(db):
    """
    Print the count of each nature of incidents.
    """
    cursor = db.cursor()
    cursor.execute('SELECT nature, COUNT(*) FROM incidents GROUP BY nature ORDER BY COUNT(*) DESC')
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}|{row[1]}")

def main(url):
    """
    Main function to fetch, extract, and store incident data from a PDF URL.
    """
    # Download data
    incident_data = fetchincidents(url)

    # Extract data
    incidents = extractincidents(incident_data)

    # Create new database
    db = createdb()

    # Insert data into the database
    populatedb(db, incidents)

    # Print incident counts
    status(db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="Incident summary URL.")
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
