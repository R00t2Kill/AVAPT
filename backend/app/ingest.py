import json
import os
from datetime import datetime
import pkgutil

SAMPLE_DATA_PATH = "/app/data/sample_devices.json"

def ingest_shodan_sample_safe(opensearch_helper):
    """
    Load the bundled sample JSON into OpenSearch.
    Returns the number of documents indexed.
    """
    # sample bundle is located at /app/data/sample_devices.json (copied into container)
    try:
        with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    except FileNotFoundError:
        # try relative path if running outside container
        here = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_devices.json")
        with open(here, "r", encoding="utf-8") as f:
            items = json.load(f)
    count = 0
    for it in items:
        doc = {
            "ip": it.get("ip"),
            "port": it.get("port"),
            "banner": it.get("banner"),
            "vendor": it.get("vendor"),
            "model": it.get("model"),
            "firmware": it.get("firmware"),
            "lab": it.get("lab", False),
            "cves": it.get("cves", []),
        }
        opensearch_helper.index_device(doc)
        count += 1
    return count

def ingest_shodan_query_safe(opensearch_helper, query, api_key):
    """
    Read-only Shodan query ingestion. This function calls Shodan API
    and indexes only the metadata received; it does NOT connect to devices.
    (Note: this function is meant for authorized use / demo with API key.)
    """
    import shodan
    sh = shodan.Shodan(api_key)
    results = sh.search(query)
    count = 0
    for m in results.get("matches", []):
        doc = {
            "ip": m.get("ip_str"),
            "port": m.get("port"),
            "banner": m.get("data")[:2000] if m.get("data") else "",
            "vendor": None,
            "model": None,
            "firmware": None,
            "lab": False,
            "cves": []
        }
        opensearch_helper.index_device(doc)
        count += 1
    return count
