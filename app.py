from fastapi import FastAPI, Query
from google.cloud import discoveryengine_v1
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from a .env file
load_dotenv()

# -------------------------
# Vertex AI Search Configuration
# -------------------------
# Load sensitive information from environment variables
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "true-artwork-472115-u8")
LOCATION = "global"  # Important: match your data store region
DATASTORE_ID = "employee-data_1758380015537"
APP_ID = "employee-search_1758376227088"
SERVING_CONFIG_ID = "default_config"  # usually default unless custom
KEY_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/home/patilswapnil0198/project/employee-search/true-artwork-472115-u8-4552e343cdfd.json")

# Create credentials and client
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = discoveryengine_v1.SearchServiceClient(credentials=credentials)

# -------------------------
# Helper to get serving config path
# -------------------------
def get_serving_config_path():
    """Constructs the full path to the serving config."""
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/dataStores/{DATASTORE_ID}/servingConfigs/{SERVING_CONFIG_ID}"


# -------------------------
# Search endpoint for raw JSON
# -------------------------
@app.get("/search_clean")
def search_clean(q: str = Query(..., description="Search query")):
    """
    Performs a search on the Vertex AI Search data store, returning raw JSON.
    Args:
        q: The search query string.
    Returns:
        A JSON response with the search results or an error message.
    """
    serving_config_path = get_serving_config_path()

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        query=q
    )

    try:
        response = client.search(request=request)
        results = []
        for result in response.results:
            item = {}
            if result.document:
                if hasattr(result.document, 'struct_data'):
                    item['id'] = result.document.id
                    item['fields'] = result.document.struct_data
                results.append(item)
        return {"results": results}

    except Exception as e:
        return {"error": str(e)}


# -------------------------
# Search endpoint for pretty-printed results
# -------------------------
@app.get("/search_pretty")
def search_pretty(q: str = Query(..., description="Search query")):
    """
    Performs a search and returns the results in a formatted string.
    Args:
        q: The search query string.
    Returns:
        A JSON response with a formatted result string.
    """
    serving_config_path = get_serving_config_path()

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        query=q
    )

    try:
        response = client.search(request=request)
        pretty_results = []
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                fields = result.document.document.struct_data
                formatted_string = f"Employee ID: {result.document.id}\n"
                for key, value in fields.items():
                    formatted_string += f"  - {key}: {value}\n"
                pretty_results.append(formatted_string)
        
        if not pretty_results:
            return {"result": "No matching employees found."}
        else:
            return {"result": "\n\n---\n\n".join(pretty_results)}

    except Exception as e:
        return {"error": str(e)}


# -------------------------
# Search endpoint for table formatted results
# -------------------------
@app.get("/search_table")
def search_table(q: str = Query(..., description="Search query")):
    """
    Performs a search and returns the results in a table-friendly JSON format.
    Args:
        q: The search query string.
    Returns:
        A JSON response with headers and rows for table display.
    """
    serving_config_path = get_serving_config_path()

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        query=q
    )

    try:
        response = client.search(request=request)
        
        all_fields = set()
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                all_fields.update(result.document.struct_data.keys())
        
        headers = sorted(list(all_fields))
        if 'id' not in headers:
            headers.insert(0, 'id')

        rows = []
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                row_data = {}
                row_data['id'] = result.document.id
                for key in headers:
                    if key != 'id':
                        row_data[key] = result.document.struct_data.get(key, None)
                rows.append(row_data)

        if not rows:
            return {"headers": [], "rows": []}
        else:
            return {"headers": headers, "rows": rows}

    except Exception as e:
        return {"error": str(e)}


# -------------------------
# New endpoint for numerical search
# -------------------------
@app.get("/search_by_salary")
def search_by_salary(salary: float = Query(..., description="Search by exact salary")):
    """
    Performs a search using a numerical filter on the 'Salary' field.
    Args:
        salary: The exact salary amount to search for.
    Returns:
        A JSON response with the search results in a table-friendly format.
    """
    serving_config_path = get_serving_config_path()

    # Construct the filter string for the numerical lookup
    filter_string = f"Salary = {salary}"

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        filter=filter_string
    )

    try:
        response = client.search(request=request)
        
        all_fields = set()
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                all_fields.update(result.document.struct_data.keys())
        
        headers = sorted(list(all_fields))
        if 'id' not in headers:
            headers.insert(0, 'id')

        rows = []
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                row_data = {}
                row_data['id'] = result.document.id
                for key in headers:
                    if key != 'id':
                        row_data[key] = result.document.struct_data.get(key, None)
                rows.append(row_data)

        if not rows:
            return {"headers": [], "rows": []}
        else:
            return {"headers": headers, "rows": rows}

    except Exception as e:
        return {"error": str(e)}


# -------------------------
# New endpoint for date-based search
# -------------------------
@app.get("/search_by_joining_date")
def search_by_joining_date(joining_date: str = Query(..., description="Search by exact joining date (YYYY-MM-DD)")):
    """
    Performs a search using a filter on the 'Joining_Date' field.
    Args:
        joining_date: The exact joining date (e.g., '2023-01-15').
    Returns:
        A JSON response with the search results in a table-friendly format.
    """
    serving_config_path = get_serving_config_path()

    # Corrected filter string with double quotes for the date string.
    filter_string = f"Joining_Date = \"{joining_date}\""

    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        filter=filter_string
    )

    try:
        response = client.search(request=request)
        
        all_fields = set()
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                all_fields.update(result.document.struct_data.keys())
        
        headers = sorted(list(all_fields))
        if 'id' not in headers:
            headers.insert(0, 'id')

        rows = []
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                row_data = {}
                row_data['id'] = result.document.id
                for key in headers:
                    if key != 'id':
                        row_data[key] = result.document.struct_data.get(key, None)
                rows.append(row_data)

        if not rows:
            return {"headers": [], "rows": []}
        else:
            return {"headers": headers, "rows": rows}

    except Exception as e:
        return {"error": str(e)}

# -------------------------
# New endpoint for department-based search
# -------------------------
@app.get("/search_by_department")
def search_by_department(department: str = Query(..., description="Search by exact department name")):
    """
    Performs a search using a filter on the 'Department' field.
    Args:
        department: The exact department name (e.g., 'HR').
    Returns:
        A JSON response with the search results in a table-friendly format.
    """
    serving_config_path = get_serving_config_path()

    # The Department field is not filterable. We must use a keyword query instead.
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        query=department
    )

    try:
        response = client.search(request=request)
        
        all_fields = set()
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                all_fields.update(result.document.struct_data.keys())
        
        headers = sorted(list(all_fields))
        if 'id' not in headers:
            headers.insert(0, 'id')

        rows = []
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                row_data = {}
                row_data['id'] = result.document.id
                for key in headers:
                    if key != 'id':
                        row_data[key] = result.document.struct_data.get(key, None)
                rows.append(row_data)

        if not rows:
            return {"headers": [], "rows": []}
        else:
            return {"headers": headers, "rows": rows}

    except Exception as e:
        return {"error": str(e)}

# -------------------------
# New endpoint for searching by name
# -------------------------
@app.get("/search_by_name")
def search_by_name(name: str = Query(..., description="Search by exact employee name")):
    """
    Performs a search using a keyword query on the 'Name' field.
    Args:
        name: The exact name to search for.
    Returns:
        A JSON response with the search results in a table-friendly format.
    """
    serving_config_path = get_serving_config_path()
    
    # We use a keyword query for the name, as it's a text field.
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path,
        query=name
    )
    
    try:
        response = client.search(request=request)
        
        all_fields = set()
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                all_fields.update(result.document.struct_data.keys())
        
        headers = sorted(list(all_fields))
        if 'id' not in headers:
            headers.insert(0, 'id')
        
        rows = []
        for result in response.results:
            if result.document and hasattr(result.document, 'struct_data'):
                row_data = {}
                row_data['id'] = result.document.id
                for key in headers:
                    if key != 'id':
                        row_data[key] = result.document.struct_data.get(key, None)
                rows.append(row_data)
        
        if not rows:
            return {"headers": [], "rows": []}
        else:
            return {"headers": headers, "rows": rows}

    except Exception as e:
        return {"error": str(e)}
