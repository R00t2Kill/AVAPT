from opensearchpy import OpenSearch
import os
import time

class OpenSearchHelper:
    def __init__(self, url="http://localhost:9200"):
        self.url = url
        self.client = OpenSearch([self.url], timeout=30)
        self.index = "devices"
        self.cve_index = "cve_map"

    def create_index_mappings(self):
        if not self.client.indices.exists(self.index):
            mapping = {
                "mappings": {
                    "properties": {
                        "ip": {"type": "ip"},
                        "port": {"type": "integer"},
                        "banner": {"type": "text"},
                        "vendor": {"type": "keyword"},
                        "model": {"type": "keyword"},
                        "firmware": {"type": "keyword"},
                        "cves": {"type": "keyword"},
                        "cvss": {"type": "float"},
                        "geo": {"properties": {"lat": {"type": "float"}, "lon": {"type": "float"}}},
                        "lab": {"type": "boolean"},
                        "first_seen": {"type": "date"}
                    }
                }
            }
            self.client.indices.create(self.index, body=mapping)
        if not self.client.indices.exists(self.cve_index):
            self.client.indices.create(self.cve_index, body={"mappings":{"properties":{"product":{"type":"keyword"},"cve":{"type":"keyword"},"cvss":{"type":"float"}}}})

    def index_device(self, doc, id=None):
        doc.setdefault("first_seen", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        res = self.client.index(self.index, body=doc, id=id)
        return res

    def search_devices(self, q=None, size=100):
        if not q:
            res = self.client.search(index=self.index, size=size, body={"query":{"match_all":{}}})
        else:
            res = self.client.search(index=self.index, size=size, body={"query":{"multi_match":{"query": q, "fields":["banner","vendor","model","firmware"]}}})
        hits = [h["_source"] for h in res["hits"]["hits"]]
        return {"total": res["hits"]["total"]["value"], "devices": hits}

    def index_cve(self, product, cve, cvss=0.0):
        doc = {"product": product, "cve": cve, "cvss": float(cvss)}
        return self.client.index(self.cve_index, body=doc)

    def search_cve(self, token, size=20):
        res = self.client.search(index=self.cve_index, size=size, body={"query":{"match":{"product": {"query": token, "fuzziness": "AUTO"}}}})
        hits = [h["_source"] for h in res["hits"]["hits"]]
        return hits
