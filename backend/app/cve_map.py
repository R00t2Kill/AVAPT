from .opensearch import OpenSearchHelper
import re

# Simple substring matching against cve_map index
def match_cves_text(text, max_results=10):
    oh = OpenSearchHelper()
    tokens = set(re.findall(r"[A-Za-z0-9\-\_\.]{3,}", text or ""))
    matches = []
    for t in tokens:
        res = oh.search_cve(t, size=5)
        for r in res:
            if r not in matches:
                matches.append(r)
                if len(matches) >= max_results:
                    break
        if len(matches) >= max_results:
            break
    return matches
