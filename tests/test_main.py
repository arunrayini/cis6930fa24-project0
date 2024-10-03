import pytest
import sqlite3
from unittest.mock import patch, Mock
from unittest.mock import patch, Mock, mock_open
from project0.main import fetchincidents, extractincidents, createdb, populatedb, status

MOCK_PDF_CONTENT = b"%PDF-1.4"  # Mocked binary data to represent PDF data

@pytest.fixture(scope="function")
def setup_db():
    """Setup a temporary SQLite database for testing."""
    conn = sqlite3.connect(':memory:')  # Use an in-memory database for testing
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
    yield conn
    conn.close()

def test_fetchincidents():
    """Test the fetchincidents function to ensure it correctly fetches the PDF content."""
    url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.read.return_value = MOCK_PDF_CONTENT

        with patch("tempfile.mkstemp", return_value=(None, "/tmp/mockfile.pdf")) as mock_tempfile:
            with patch("builtins.open", mock_open()) as mock_file:
                data = fetchincidents(url)
                assert data == "/tmp/mockfile.pdf"

def test_populatedb(setup_db):
    """Test populatedb to ensure it inserts data into the SQLite database correctly."""
    conn = setup_db
    # Use a list of tuples instead of a DataFrame
    incidents = [
        ('8/1/2024 0:01', '2024-00000001', '123 MAIN ST', 'Traffic Stop', 'OK0140200'),
        ('8/1/2024 0:05', '2024-00000002', '456 OAK ST', 'Welfare Check', 'OK0140200')
    ]

    populatedb(conn, incidents)

    # Verify data was inserted correctly
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert rows[0][0] == '8/1/2024 0:01'
    assert rows[1][0] == '8/1/2024 0:05'

def test_status(setup_db, capsys):
    """Test the status function to ensure it prints the incident nature counts correctly."""
    conn = setup_db
    # Use a list of tuples instead of a DataFrame
    incidents = [
        ('8/1/2024 0:01', '2024-00000001', '123 MAIN ST', 'Traffic Stop', 'OK0140200'),
        ('8/1/2024 0:05', '2024-00000002', '456 OAK ST', 'Welfare Check', 'OK0140200'),
        ('8/1/2024 0:10', '2024-00000003', '789 PINE ST', 'Traffic Stop', 'OK0140201')
    ]

    populatedb(conn, incidents)

    # Capture the output of the status function
    status(conn)
    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    # Verify the status output is correct
    assert output_lines[0] == "Traffic Stop|2"
    assert output_lines[1] == "Welfare Check|1"