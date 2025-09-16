from fastapi import FastAPI
import re
from datetime import datetime

app = FastAPI()

# -------------------------
# Sample Employee Data
# -------------------------
SAMPLE_DATA = """
ID	Name	Email	Department	Joining Date	Salary
1	Swapnil Patil	swapnil@example.com	Engineering	2023-01-15	75000
2	Ruchita Patil	ruchita@example.com	Marketing	2022-06-20	65000
3	Amit Sharma	amit@example.com	Sales	2021-11-05	60000
4	Sneha Verma	sneha@example.com	HR	2020-09-12	55000
"""

# -------------------------
# Root endpoint
# -------------------------
@app.get("/")
def root():
    return {
        "message": "FastAPI Employee Search running. Use /search_clean?q=your_query"
    }

# -------------------------
# /search_clean endpoint
# -------------------------
@app.get("/search_clean")
def search_clean(q: str):
    """
    Search the sample employee data and return matching rows.
    Works for any query: Name, Department, Salary, etc.
    """
    # Split lines and remove empty lines
    lines = [line.strip() for line in SAMPLE_DATA.split("\n") if line.strip()]
    if len(lines) < 2:
        return {"results": [], "message": "Not enough data"}

    # Header and data rows
    header = re.split(r'\t|\s{2,}', lines[0])
    data_rows = lines[1:]
    results = []

    for row in data_rows:
        fields = re.split(r'\t|\s{2,}', row)
        if len(fields) != len(header):
            continue
        row_dict = dict(zip(header, fields))

        # Type conversion
        if 'Salary' in row_dict:
            try:
                row_dict['Salary'] = int(row_dict['Salary'])
            except:
                pass
        if 'Joining Date' in row_dict:
            try:
                row_dict['Joining Date'] = datetime.strptime(
                    row_dict['Joining Date'], '%Y-%m-%d'
                ).date().isoformat()
            except:
                pass

        # Include row if query matches any field
        if any(q.lower() in str(v).lower() for v in row_dict.values()):
            results.append(row_dict)

    if not results:
        return {"results": [], "message": "No matching data found"}

    return {"results": results}
