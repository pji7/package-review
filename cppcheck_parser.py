import xml.etree.ElementTree as ET
import csv

# Path configuration.
input_xml = "cppcheck.xml"
output_csv = "cppcheck_cwe_warnings.csv"


tree = ET.parse(input_xml)
root = tree.getroot()

results = []

for error in root.findall("errors/error"):
    cwe = error.get("cwe")
    if cwe:  # Only extract alerts include CWE info.
        error_id = error.get("id")
        severity = error.get("severity")
        msg = error.get("msg")
        verbose = error.get("verbose")

        # For multiple locations listed in one alerts, keep the first one only.
        # [TODO] Conduct a better way to combine multiple locations in same alert.
        location = error.find("location")
        if location is not None:
            file_path = location.get("file")
            line = location.get("line")
            column = location.get("column")
        else:
            file_path = line = column = ""

        results.append([
            cwe, error_id, severity, msg, verbose,
            file_path, line, column
        ])

# Write results into CSV file.
with open(output_csv, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["CWE", "Error ID", "Severity", "Message", "Verbose", "File", "Line", "Column"])
    writer.writerows(results)

print(f"Extracting process completed: {output_csv}")
