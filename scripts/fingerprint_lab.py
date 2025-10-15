#!/usr/bin/env python3
"""
Lab-only fingerprinting script.
This script WILL REFUSE to run unless --lab flag is provided.
It uses conservative nmap flags and only targets ports 80,443,554.
"""

import argparse
import subprocess
import shlex
import json
import requests
import os
import sys

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

def run_nmap(target):
    # Conservative nmap: single-target, limited ports, low retries
    cmd = f"nmap -Pn -sS -p 80,443,554 --max-retries 1 --host-timeout 30s {target} -oJ -"
    print("Running:", cmd)
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=120)
    return proc.stdout

def http_head(target, port=80):
    try:
        url = f"http://{target}:{port}"
        resp = requests.head(url, timeout=5)
        headers = dict(resp.headers)
        return {"status_code": resp.status_code, "headers": headers}
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="IP of lab device")
    parser.add_argument("--lab", action="store_true", help="Enable lab mode")
    args = parser.parse_args()

    if not args.lab:
        print("Refusing to run. This script is lab-only. Use --lab to confirm.")
        sys.exit(1)

    target = args.target
    nmap_output = run_nmap(target)
    try:
        nmap_json = json.loads(nmap_output)
    except Exception:
        nmap_json = {"raw": nmap_output}

    http_info = http_head(target, port=80)
    doc = {
        "ip": target,
        "port": 80,
        "banner": nmap_json,
        "vendor": None,
        "model": None,
        "firmware": None,
        "lab": True,
        "cves": []
    }
    # Index into OpenSearch via backend API (do not call device)
    resp = requests.post(f"{API_BASE}/api/devices", json=doc) if False else None
    # The backend does not provide POST /api/devices; suggest to use opensearch client scripts or verify indexing in other ways.
    # For now, save output locally:
    with open(f"fingerprint_{target}.json", "w", encoding="utf-8") as f:
        json.dump({"nmap": nmap_json, "http": http_info}, f, indent=2)
    print(f"Saved fingerprint to fingerprint_{target}.json")

if __name__ == "__main__":
    main()
