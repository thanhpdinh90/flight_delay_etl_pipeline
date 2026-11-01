import csv
import io
import zipfile
from pathlib import Path

import requests

# January 2025 flight data from BTS
YEAR = 2025
MONTH = 1

url = (
    "https://transtats.bts.gov/PREZIP/"
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"
    f"{YEAR}_{MONTH}.zip"
)

columns = [
    "FlightDate",
    "Reporting_Airline",
    "Flight_Number_Reporting_Airline",
    "Origin",
    "Dest",
    "DepDelay",
    "ArrDelay",
    "Cancelled",
    "Diverted",
]

output_file = Path("data/flights_2025_01_sample.csv")
output_file.parent.mkdir(parents=True, exist_ok=True)

print("Downloading January 2025 flight data...")

response = requests.get(url, timeout=180)
response.raise_for_status()

with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
    csv_name = next(
        name for name in archive.namelist()
        if name.lower().endswith(".csv")
    )

    with archive.open(csv_name) as source:
        reader = csv.DictReader(
            io.TextIOWrapper(source, encoding="utf-8-sig")
        )

        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()

            count = 0
            for row in reader:
                writer.writerow({col: row[col] for col in columns})
                count += 1

                if count == 1000:
                    break

print(f"Success! Saved {count} flights to {output_file}")
