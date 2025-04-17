import csv

# Input and output filenames
csv_filename = "company_names_identifiers_urls.csv"  # Replace with your actual file name
output_filename = "company_identifier.csv"

data = []

with open(csv_filename, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    headers = next(reader)  # Read headers
    data.append(headers + ["Sector", "Identifier"])  # Add new columns

    for row in reader:
        if len(row) < 3:
            continue  # Skip invalid rows

        company_name, identifier_from_csv, url = row
        parts = url.rstrip('/').split('/')  # Split URL

        if len(parts) >= 3:
            sector = parts[-3]  # Extract sector (3rd last part)
            identifier = parts[-2]  # Extract identifier (2nd last part)
        else:
            sector = "N/A"
            identifier = "N/A"  # Handle malformed URLs
        
        data.append(row + [sector, identifier])

# Save the updated CSV
with open(output_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f"✅ Extracted sector and identifier saved to {output_filename}")
