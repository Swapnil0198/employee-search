import csv
import json

csv_file = "employee.csv"
jsonl_file = "employees.jsonl"

with open(csv_file, "r", encoding="utf-8") as f_in, open(jsonl_file, "w", encoding="utf-8") as f_out:
    reader = csv.DictReader(f_in)
    for row in reader:
        row["Salary"] = int(row["Salary"])   # make Salary an integer
        row["id"] = row["ID"]                # add 'id' field
        row.pop("ID", None)                  # remove the original ID field if you want
        f_out.write(json.dumps(row) + "\n")  # directly dump the flat dict

print(f"Converted {csv_file} → {jsonl_file}")

