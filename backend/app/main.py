import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List
from .opensearch import OpenSearchHelper
from .ingest import ingest_shodan_sample_safe, ingest_shodan_query_safe
from .cve_map import match_cves_text
from pydantic import BaseModel

OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
LAB_MODE = os.environ.get("LAB_MODE", "false").lower() == "true"

es = OpenSearchHelper(OPENSEARCH_URL)
app = FastAPI(title="CCTV AVAPT Prototype API")

# Ensure index mappings
es.create_index_mappings()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/ingest/shodan_sample")
def ingest_shodan_sample():
    try:
        count = ingest_shodan_sample_safe(es)
        return {"status": "ok", "indexed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ShodanQuery(BaseModel):
    query: str

@app.post("/api/ingest/shodan_query")
def ingest_shodan_query(q: ShodanQuery, background: BackgroundTasks):
    api_key = os.environ.get("SHODAN_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="SHODAN_API_KEY not configured")
    background.add_task(ingest_shodan_query_safe, es, q.query, api_key)
    return {"status": "started", "query": q.query}

@app.get("/api/devices")
def get_devices(q: str = None, size: int = 100):
    res = es.search_devices(q, size)
    return res

class FingerprintRequest(BaseModel):
    target: str

@app.post("/api/fingerprint/lab")
def fingerprint_lab(req: FingerprintRequest):
    if not LAB_MODE:
        raise HTTPException(status_code=403, detail="Lab mode is disabled. Enable LAB_MODE to run lab fingerprinting.")
    return {"status": "ok", "message": f"Fingerprinting for {req.target} queued (run scripts/fingerprint_lab.py with --lab to perform locally)."}

@app.get("/api/cve/match")
def cve_match(text: str):
    matches = match_cves_text(text)
    return {"matches": matches}
