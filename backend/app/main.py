import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from .opensearch import OpenSearchHelper
from .ingest import ingest_shodan_sample_safe, ingest_shodan_query_safe
from .cve_map import match_cves_text
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
LAB_MODE = os.environ.get("LAB_MODE", "false").lower() == "true"

# Initialize OpenSearch with error handling
try:
    es = OpenSearchHelper(OPENSEARCH_URL)
    # Test connection and create mappings
    if es.client.ping():
        logger.info("Successfully connected to OpenSearch")
        es.create_index_mappings()
    else:
        logger.error("Failed to connect to OpenSearch")
        es = None
except Exception as e:
    logger.error(f"OpenSearch initialization failed: {e}")
    es = None

app = FastAPI(title="CCTV AVAPT Prototype API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ShodanQuery(BaseModel):
    query: str

class FingerprintRequest(BaseModel):
    target: str

class ROERequest(BaseModel):
    name: str
    assessment_type: str
    dates: dict
    scope: str
    allowed_activities: List[str]
    restricted_actions: List[str]
    contacts: str
    emergency_procedure: str

@app.get("/")
async def root():
    return {"message": "CCTV AVAPT Prototype API", "status": "running"}

@app.get("/health")
def health():
    """Health check endpoint"""
    opensearch_status = "connected" if es and es.client.ping() else "disconnected"
    return {
        "status": "ok",
        "opensearch": opensearch_status,
        "lab_mode": LAB_MODE
    }

@app.post("/api/ingest/shodan_sample")
def ingest_shodan_sample():
    """Ingest sample Shodan data"""
    if not es:
        raise HTTPException(status_code=500, detail="OpenSearch not available")
    
    try:
        count = ingest_shodan_sample_safe(es)
        return {"status": "ok", "indexed": count}
    except Exception as e:
        logger.error(f"Error ingesting sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest/shodan_query")
def ingest_shodan_query(q: ShodanQuery, background: BackgroundTasks):
    """Ingest Shodan data using query"""
    if not es:
        raise HTTPException(status_code=500, detail="OpenSearch not available")
    
    api_key = os.environ.get("SHODAN_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="SHODAN_API_KEY not configured")
    
    background.add_task(ingest_shodan_query_safe, es, q.query, api_key)
    return {"status": "started", "query": q.query}

@app.post("/api/ingest/cves")
def ingest_cves():
    """Ingest CVE data"""
    try:
        # This would call your CVE ingestion logic
        # For now, return success
        return {"status": "success", "message": "CVE ingestion endpoint"}
    except Exception as e:
        logger.error(f"Error ingesting CVEs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices")
def get_devices(q: str = None, size: int = 100):
    """Get devices with optional search"""
    if not es:
        return []
    
    try:
        res = es.search_devices(q, size)
        return res
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return []

@app.get("/api/devices/search")
def search_devices(q: str = "", size: int = 50):
    """Search devices (alias for /api/devices)"""
    if not es:
        return []
    
    try:
        res = es.search_devices(q, size)
        return res
    except Exception as e:
        logger.error(f"Error searching devices: {e}")
        return []

@app.get("/api/devices/vulnerable")
def get_vulnerable_devices():
    """Get vulnerable devices"""
    if not es:
        return []
    
    try:
        # This would query for devices with vulnerabilities
        # For now, return all devices
        res = es.search_devices(None, 100)
        return res
    except Exception as e:
        logger.error(f"Error getting vulnerable devices: {e}")
        return []

@app.get("/api/cves")
def get_cves():
    """Get CVE data"""
    try:
        # Return sample CVE data for now
        sample_cves = [
            {
                "cve_id": "CVE-2024-1234",
                "description": "Camera firmware buffer overflow vulnerability",
                "cvss_score": 8.2,
                "published_date": "2024-01-15",
                "affected_devices": ["Camera Firmware v2.1.3"]
            },
            {
                "cve_id": "CVE-2024-1235",
                "description": "Default credentials in web interface",
                "cvss_score": 7.5,
                "published_date": "2024-01-10",
                "affected_devices": ["Multiple CCTV models"]
            }
        ]
        return sample_cves
    except Exception as e:
        logger.error(f"Error getting CVEs: {e}")
        return []

@app.post("/api/fingerprint/lab")
def fingerprint_lab(req: FingerprintRequest):
    """Fingerprint lab target"""
    if not LAB_MODE:
        raise HTTPException(status_code=403, detail="Lab mode is disabled. Enable LAB_MODE to run lab fingerprinting.")
    return {"status": "ok", "message": f"Fingerprinting for {req.target} queued (run scripts/fingerprint_lab.py with --lab to perform locally)."}

@app.get("/api/cve/match")
def cve_match(text: str):
    """Match CVEs against text"""
    try:
        matches = match_cves_text(text)
        return {"matches": matches}
    except Exception as e:
        logger.error(f"Error matching CVEs: {e}")
        return {"matches": []}

@app.get("/api/roes/template")
def get_roe_template():
    """Get ROE template"""
    template = """
    # Rules of Engagement Template
    
    ## Assessment Details
    - **Name**: [Assessment Name]
    - **Type**: [Assessment Type]
    - **Dates**: [Start Date] to [End Date]
    
    ## Scope
    [Target systems, IP ranges, domains]
    
    ## Allowed Activities
    - [List of permitted testing activities]
    
    ## Restricted Actions
    - [List of prohibited activities]
    
    ## Contacts
    - [Primary contact information]
    
    ## Emergency Procedures
    - [Steps to take in case of issues]
    """
    return template

@app.post("/api/roes")
def submit_roe(roe: ROERequest):
    """Submit ROE data"""
    try:
        # In a real implementation, you would save this to a database
        # For now, just return the received data
        return {
            "status": "success",
            "message": "ROE submitted successfully",
            "data": roe.dict()
        }
    except Exception as e:
        logger.error(f"Error submitting ROE: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
def get_stats():
    """Get system statistics"""
    if not es:
        return {
            "total_devices": 0,
            "vulnerable_devices": 0,
            "total_cves": 0
        }
    
    try:
        # Get device count
        devices = es.search_devices(None, 1000)
        total_devices = len(devices)
        
        # Count vulnerable devices (simplified)
        vulnerable_devices = len([d for d in devices if d.get('vulnerabilities')])
        
        return {
            "total_devices": total_devices,
            "vulnerable_devices": vulnerable_devices,
            "total_cves": 2  # Sample CVE count
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "total_devices": 0,
            "vulnerable_devices": 0,
            "total_cves": 0
        }