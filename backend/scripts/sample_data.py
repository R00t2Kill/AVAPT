#!/usr/bin/env python3
"""
Load bundled sample devices into OpenSearch by calling backend API.
"""
import argparse
import requests
import os

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-sample", action="store_true")
    args = parser.parse_args()
    if args.load_sample:
        resp = requests.post(f"{API_BASE}/api/ingest/shodan_sample")
        print(resp.status_code, resp.text)
    else:
        print("Use --load-sample to load bundled sample data")
