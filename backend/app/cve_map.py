import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

# Sample CVE database (in production, this would be a real database)
SAMPLE_CVES = [
    {
        "cve_id": "CVE-2024-1234",
        "description": "Camera firmware buffer overflow vulnerability",
        "cvss_score": 8.2,
        "keywords": ["camera", "firmware", "buffer", "overflow", "cctv"]
    },
    {
        "cve_id": "CVE-2024-1235", 
        "description": "Default credentials in web interface",
        "cvss_score": 7.5,
        "keywords": ["default", "credentials", "web", "interface", "admin", "password"]
    },
    {
        "cve_id": "CVE-2024-1236",
        "description": "RTSP stream authentication bypass",
        "cvss_score": 9.1,
        "keywords": ["rtsp", "stream", "authentication", "bypass", "camera"]
    }
]

def match_cves_text(text: str) -> List[Dict[str, Any]]:
    """Match CVEs against input text"""
    if not text:
        return []
    
    text_lower = text.lower()
    matches = []
    
    for cve in SAMPLE_CVES:
        score = 0
        matched_keywords = []
        
        # Check for keyword matches
        for keyword in cve['keywords']:
            if keyword in text_lower:
                score += 1
                matched_keywords.append(keyword)
        
        # Check for CVE ID pattern
        if re.search(r'cve[-\_]?\d{4}[-\_]?\d+', text_lower, re.IGNORECASE):
            score += 2
        
        if score > 0:
            matches.append({
                **cve,
                'match_score': score,
                'matched_keywords': matched_keywords
            })
    
    # Sort by match score (descending)
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches