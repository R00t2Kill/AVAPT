#!/usr/bin/env python3
"""
Safe Shodan ingestion script.
Modes:
 - --sample : load bundled sample devices into backend via API (safe)
 - --query "<shodan query>": perform read-only Shodan search and push metadata to backend (requires SHODAN_API_KEY env var)
"""
import argparse
import os
import requests
import json

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

def load_sample():
    resp = requests.post(f"{API_BASE}/api/ingest/shodan_sample")
    print(resp.json())

def run_query(query):
    key = os.environ.get("SHODAN_API_KEY")
    if not key:
        print("SHODAN_API_KEY not set in env. Aborting.")
        return
    resp = requests.post(f"{API_BASE}/api/ingest/shodan_query", json={"query": query})
    print(resp.status_code, resp.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--query", type=str, default=None)
    args = parser.parse_args()
    if args.sample:
        load_sample()
    elif args.query:
        run_query(args.query)
    else:
        print("No action specified. Use --sample or --query '<term>'.")
