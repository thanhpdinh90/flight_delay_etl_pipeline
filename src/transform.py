import pandas as pd
from pathlib import Path

# Define input and output files
input_file = Path("data/flights_2025_01_sample.csv")
output_file = Path("data/flights_2025_01_cleaned.csv")

# Read the extracted flight data
print("Loading flight data...")

df = pd.read_csv(input_file)
original_count = len(df)

print(f"Original records: {original_count}")

# Clean text columns
text_columns = ["Reporting_Airline", "Origin", "Dest"]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip().str.upper()

# Convert dates and numeric columns
df["FlightDate"] = pd.to_datetime(
    df["FlightDate"], errors="coerce"
)

numeric_columns = [
    "DepDelay",
    "ArrDelay",
    "Cancelled",
    "Diverted",
    "Flight_Number_Reporting_Airline",
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove exact duplicate rows
df = df.drop_duplicates().copy()

# Check essential information
required_columns = [
    "FlightDate",
    "Reporting_Airline",
    "Origin",
    "Dest",
]

df = df.dropna(subset=required_columns).copy()

# Create analytical columns

# BTS commonly uses 15+ minutes for delay reporting.
df["IsDelayed"] = (
    (df["ArrDelay"] >= 15)
    & (df["Cancelled"] == 0)
    & (df["Diverted"] == 0)
).astype("Int64")

# Missing arrival delay is not automatically on time.
unknown = (
    df["ArrDelay"].isna()
    | df["Cancelled"].isna()
    | df["Diverted"].isna()
)
df.loc[unknown, "IsDelayed"] = pd.NA

# Create a flight status category
def classify_flight(row):
    if row["Cancelled"] == 1:
        return "Cancelled"
    if row["Diverted"] == 1:
        return "Diverted"
    if pd.isna(row["ArrDelay"]):
        return "Unknown"
    if row["ArrDelay"] >= 15:
        return "Delayed"
    return "On Time"

df["FlightStatus"] = df.apply(classify_flight, axis=1)

# Extract useful date information
df["Year"] = df["FlightDate"].dt.year
df["Month"] = df["FlightDate"].dt.month
df["DayOfWeek"] = df["FlightDate"].dt.day_name()

# Save cleaned data
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

# Display transformation results
print("\nTransformation complete!")
print(f"Original records: {original_count}")
print(f"Cleaned records: {len(df)}")
print(f"Exact duplicates removed: {original_count - len(df)}")
print("\nFlight status summary:")
print(df["FlightStatus"].value_counts(dropna=False))
print(f"\nSaved cleaned data to: {output_file}")