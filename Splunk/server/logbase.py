import requests
from dotenv import load_dotenv
import os

load_dotenv()

SPLUNK_HOST = os.getenv("SPLUNK_HOST")
SPLUNK_USERNAME = os.getenv("SPLUNK_USERNAME")
SPLUNK_PASSWORD = os.getenv("SPLUNK_PASSWORD")

def run_splunk_query(spl_query: str):
    """Run an SPL query via Splunk REST API."""
    url = f"{SPLUNK_HOST}/services/search/jobs"
    data = {
        "search": spl_query,
        "output_mode": "json"
    }

    response = requests.post(url, auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD), data=data, verify=False)
    if response.status_code != 201:
        raise Exception(f"Failed to create search job: {response.text}")

    sid = response.json()["sid"]
    results_url = f"{SPLUNK_HOST}/services/search/jobs/{sid}/results?output_mode=json"

    # Wait for job completion
    import time
    time.sleep(5)

    results = requests.get(results_url, auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD), verify=False)
    return results.json()
