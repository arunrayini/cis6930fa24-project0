import pytest
import sqlite3
from unittest.mock import patch, Mock
from project0.main import fetchincidents, extractincidents, createdb, populatedb, status

MOCK_INCIDENT_DATA = b"%PDF-1.4"  # Mocked binary data to represent PDF data

@pytest.fixture(scope="function")
def setup_db():
    """Setup a temporary SQLite database for testing."""
    conn = sqlite3.connect(':memory:')  # Use an in-memory database for testing
    createdb(conn)
    yield conn
    conn.close()

def test_fetchincidents():
    """Test if fetchincidents correctly downloads PDF data."""
    url = "https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-01_daily_incident_summary.pdf"
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.read.return_value = MOCK_INCIDENT_DATA
        data = fetchincidents(url)
        assert data == MOCK_INCIDENT_DATA



def test_populatedb(setup_db):
    """Test if the populatedb function correctly inserts data into the database."""
    conn = setup_db
    incidents = [
        {'incident_time': '9/1/2024 0:05', 'incident_number': '2024-00063623', 'incident_location': '1049 12TH AVE NE', 'nature': 'Welfare Check', 'incident_ori': 'OK0140200'},
        {'incident_time': '9/1/2024 0:15', 'incident_number': '2024-00063624', 'incident_location': '123 MAIN ST', 'nature': 'Traffic Stop', 'incident_ori': 'OK0140201'}
    ]
    populatedb(conn, incidents)

    # Verify data was inserted correctly
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert rows[0][0] == '9/1/2024 0:05'
    assert rows[1][0] == '9/1/2024 0:15'

def test_status(setup_db, capsys):
    """Test if the status function correctly prints the incident nature counts."""
    conn = setup_db
    incidents = [
        {'incident_time': '9/1/2024 0:05', 'incident_number': '2024-00063623', 'incident_location': '1049 12TH AVE NE', 'nature': 'Welfare Check', 'incident_ori': 'OK0140200'},
        {'incident_time': '9/1/2024 0:15', 'incident_number': '2024-00063624', 'incident_location': '123 MAIN ST', 'nature': 'Traffic Stop', 'incident_ori': 'OK0140201'},
        {'incident_time': '9/1/2024 0:30', 'incident_number': '2024-00063625', 'incident_location': '456 OAK ST', 'nature': 'Traffic Stop', 'incident_ori': 'OK0140202'}
    ]
    populatedb(conn, incidents)

    # Capture the output of the status function
    status(conn)
    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    # Verify the status output is correct
    assert output_lines[0] == "Traffic Stop|2"
    assert output_lines[1] == "Welfare Check|1"
