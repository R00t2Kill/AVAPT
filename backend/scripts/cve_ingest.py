#!/usr/bin/env python3

import argparse
import json
import os
from opensearchpy import OpenSearch

def ingest_local(nvd_file, es_url="http://localhost:9200"):
    with open(nvd_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    client = OpenSearch([es_url])
    index = "cve_map"
    if not client.indices.exists(index):
        client.indices.create(index, body={"mappings":{"properties":{"product":{"type":"keyword"},"cve":{"type":"keyword"},"cvss":{"type":"float"}}}})
    count = 0
    # NVD feed structure varies; we look for cve.items[*].configurations.nodes[*].cpeMatch[*].cpe23Uri
    for item in data.get("CVE_Items", []):
        cve_id = item.get("cve", {}).get("CVE_data_meta", {}).get("ID")
        # try CVSS v3.1 score
        metrics = item.get("impact", {}).get("baseMetricV3", {})
        cvss = metrics.get("cvssV3", {}).get("baseScore", 0.0) if metrics else 0.0
        configs = item.get("configurations", {}).get("nodes", [])
        for node in configs:
            for match in node.get("cpe_match", []):
                cpe = match.get("cpe23Uri", "")
                if cpe:
                    doc = {"product": cpe, "cve": cve_id, "cvss": cvss}
                    client.index(index, body=doc)
                    count += 1
    print(f"Indexed {count} cpe->CVE entries into {index}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="Path to local NVD JSON file")
    parser.add_argument("--es", default="http://localhost:9200")
    args = parser.parse_args()
    if not args.local:
        print("Provide --local <nvd-json-file>")
    else:
        ingest_local(args.local, args.es)
