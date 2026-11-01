import csv
import hashlib
import json
import sqlite3
from pathlib import Path

# Define file locations
input_file = Path("data/flights_2025_01_cleaned.csv")
database_file = Path("data/flight_delays.db")

# Check that the cleaned data exists
if not input_file.exists():
    raise FileNotFoundError(
        "Cleaned CSV not found. Run transform.py first."
    )

# Connect to the SQLite database
# The file is created automatically if it does not exist.
conn = sqlite3.connect(database_file)

try:
    # Create the flights table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            record_id TEXT PRIMARY KEY,
            flight_date TEXT,
            airline TEXT,
            flight_number INTEGER,
            origin TEXT,
            destination TEXT,
            departure_delay REAL,
            arrival_delay REAL,
            cancelled INTEGER,
            diverted INTEGER,
            is_delayed INTEGER,
            flight_status TEXT,
            year INTEGER,
            month INTEGER,
            day_of_week TEXT
        )
    """)

    # Convert blank CSV values to NULL
    def clean_value(value):
        if value is None or value == "":
            return None
        return value

    # Read and load the cleaned records
    with open(input_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows_read = 0

        for row in reader:
            rows_read += 1

            # Create a fingerprint of the complete CSV record.
            # Repeated copies of the same record get the same ID.
            record_json = json.dumps(
                row, sort_keys=True, separators=(",", ":")
            )
            record_id = hashlib.sha256(
                record_json.encode("utf-8")
            ).hexdigest()

            values = (
                record_id,
                clean_value(row["FlightDate"]),
                clean_value(row["Reporting_Airline"]),
                clean_value(row["Flight_Number_Reporting_Airline"]),
                clean_value(row["Origin"]),
                clean_value(row["Dest"]),
                clean_value(row["DepDelay"]),
                clean_value(row["ArrDelay"]),
                clean_value(row["Cancelled"]),
                clean_value(row["Diverted"]),
                clean_value(row["IsDelayed"]),
                clean_value(row["FlightStatus"]),
                clean_value(row["Year"]),
                clean_value(row["Month"]),
                clean_value(row["DayOfWeek"]),
            )

            conn.execute("""
                INSERT OR IGNORE INTO flights VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, values)

    # Save changes
    conn.commit()

    # Verify the database
    total = conn.execute(
        "SELECT COUNT(*) FROM flights"
    ).fetchone()[0]

    print("SQL load completed successfully!")
    print(f"CSV records processed: {rows_read}")
    print(f"Total records in database: {total}")

finally:
    conn.close()
