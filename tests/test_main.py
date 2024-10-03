import pytest
import sqlite3
import pandas as pd
from unittest.mock import patch, Mock, mock_open
from pypdf import PdfReader
from project0.main import fetchincidents, extractincidents, createdb, populatedb, status

# Mocked PDF data 
MOCK_PDF_CONTENT = b"%PDF-1.4\n...mocked pdf content..."

@pytest.fixture(scope="function")
def setup_db():
    """Fixture to set up an in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')  # Using in-memory database
    createdb_in_memory(conn)  
    yield conn
    conn.close()

def createdb_in_memory(conn):
    """Create the 'incidents' table in an in-memory SQLite database."""
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

def test_fetchincidents():
    """Test the fetchincidents function to ensure it correctly fetches the PDF content."""
    url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.read.return_value = MOCK_PDF_CONTENT
        
        with patch("tempfile.mkstemp", return_value=(None, "/tmp/mockfile.pdf")) as mock_tempfile:
            # Using mock_open to mock file handling
            with patch("builtins.open", mock_open()) as mock_file:
                file_path = fetchincidents(url)
                assert file_path == "/tmp/mockfile.pdf"
                mock_file().write.assert_called_once_with(MOCK_PDF_CONTENT)


def test_populatedb(setup_db):
    """Test populatedb to ensure it inserts data into the SQLite database correctly."""
    conn = setup_db
    incidents = [
        {'incident_time': '8/1/2024 0:01', 'incident_number': '2024-00000001', 'incident_location': '123 MAIN ST', 'nature': 'Traffic Stop', 'incident_ori': 'OK0140200'},
        {'incident_time': '8/1/2024 0:05', 'incident_number': '2024-00000002', 'incident_location': '456 OAK ST', 'nature': 'Welfare Check', 'incident_ori': 'OK0140200'}
    ]
    
    populatedb(conn, pd.DataFrame(incidents))  # Ensuring pandas DataFrame is passed

    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert rows[0][1] == '2024-00000001'
    assert rows[1][3] == 'Welfare Check'

def test_status(setup_db, capsys):
    """Test the status function to ensure it prints the incident nature counts correctly."""
    conn = setup_db
    incidents = [
        {'incident_time': '8/1/2024 0:01', 'incident_number': '2024-00000001', 'incident_location': '123 MAIN ST', 'nature': 'Traffic Stop', 'incident_ori': 'OK0140200'},
        {'incident_time': '8/1/2024 0:05', 'incident_number': '2024-00000002', 'incident_location': '456 OAK ST', 'nature': 'Welfare Check', 'incident_ori': 'OK0140200'},
        {'incident_time': '8/1/2024 0:10', 'incident_number': '2024-00000003', 'incident_location': '789 PINE ST', 'nature': 'Traffic Stop', 'incident_ori': 'OK0140201'}
    ]

    populatedb(conn, pd.DataFrame(incidents))

    
    status(conn)
    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    
    assert output_lines[0] == "Traffic Stop|2"
    assert output_lines[1] == "Welfare Check|1"
