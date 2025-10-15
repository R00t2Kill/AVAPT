import os
from opensearchpy import OpenSearch, exceptions
import time
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenSearchHelper:
    def __init__(self, opensearch_url: str = "http://localhost:9200"):
        self.url = opensearch_url
        self.index = "avapt-devices"
        self.client = None
        self._connect()

    def _connect(self, max_retries: int = 5, delay: int = 5):
        """Connect to OpenSearch with retry logic"""
        for attempt in range(max_retries):
            try:
                self.client = OpenSearch([self.url])
                
                # Test connection
                if self.client.ping():
                    logger.info(f"Connected to OpenSearch at {self.url}")
                    return
                else:
                    logger.warning(f"OpenSearch ping failed on attempt {attempt + 1}")
                    
            except exceptions.ConnectionError as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        logger.error(f"Failed to connect to OpenSearch after {max_retries} attempts")
        self.client = None

    def create_index_mappings(self):
        """Create index with mappings if it doesn't exist"""
        if not self.client:
            logger.error("OpenSearch client not available")
            return False
            
        try:
            if not self.client.indices.exists(index=self.index):
                mapping = {
                    "settings": {
                        "index": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0  # Single node setup
                        }
                    },
                    "mappings": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "hostname": {"type": "text"},
                            "service": {"type": "keyword"},
                            "port": {"type": "integer"},
                            "status": {"type": "keyword", "null_value": "unknown"},
                            "location": {"type": "geo_point"},
                            "vulnerabilities": {
                                "type": "nested",
                                "properties": {
                                    "cve_id": {"type": "keyword"},
                                    "description": {"type": "text"},
                                    "cvss_score": {"type": "float"},
                                    "type": {"type": "keyword"}
                                }
                            },
                            "last_seen": {"type": "date"},
                            "timestamp": {"type": "date"},
                            "data": {"type": "object", "enabled": True}  # Catch-all for additional data
                        }
                    }
                }
                self.client.indices.create(index=self.index, body=mapping)
                logger.info(f"Created index: {self.index}")
            else:
                logger.info(f"Index already exists: {self.index}")
            return True
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False

    def index_device(self, device_data: Dict[str, Any]) -> bool:
        """Index a device document"""
        if not self.client:
            logger.error("OpenSearch client not available")
            return False
            
        try:
            # Ensure required fields
            if 'timestamp' not in device_data:
                device_data['timestamp'] = time.time() * 1000  # Current time in ms
                
            response = self.client.index(
                index=self.index,
                body=device_data,
                refresh=True
            )
            success = response.get('result') in ['created', 'updated']
            if success:
                logger.debug(f"Indexed device: {device_data.get('ip', 'unknown')}")
            return success
        except Exception as e:
            logger.error(f"Error indexing device: {e}")
            return False

    def search_devices(self, query: Optional[str] = None, size: int = 100) -> List[Dict[str, Any]]:
        """Search devices with optional query"""
        if not self.client:
            logger.warning("OpenSearch client not available, returning empty results")
            return []
            
        try:
            if query:
                search_body = {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "ip", 
                                "hostname", 
                                "service", 
                                "vulnerabilities.cve_id",
                                "vulnerabilities.description"
                            ],
                            "fuzziness": "AUTO"
                        }
                    },
                    "size": size
                }
            else:
                search_body = {
                    "query": {"match_all": {}},
                    "size": size,
                    "sort": [{"timestamp": {"order": "desc"}}]
                }
            
            response = self.client.search(index=self.index, body=search_body)
            hits = response['hits']['hits']
            
            # Extract _source and add _id if needed
            devices = []
            for hit in hits:
                device = hit['_source']
                device['_id'] = hit['_id']  # Include OpenSearch ID
                devices.append(device)
                
            logger.debug(f"Found {len(devices)} devices")
            return devices
            
        except exceptions.NotFoundError:
            logger.info("Index not found, returning empty results")
            return []
        except Exception as e:
            logger.error(f"Error searching devices: {e}")
            return []

    def get_all_devices(self, size: int = 100) -> List[Dict[str, Any]]:
        """Get all devices (alias for search_devices)"""
        return self.search_devices(None, size)

    def get_vulnerable_devices(self) -> List[Dict[str, Any]]:
        """Get devices with vulnerabilities"""
        if not self.client:
            logger.warning("OpenSearch client not available, returning empty results")
            return []
            
        try:
            search_body = {
                "query": {
                    "nested": {
                        "path": "vulnerabilities",
                        "query": {
                            "exists": {"field": "vulnerabilities"}
                        }
                    }
                },
                "size": 1000
            }
            
            response = self.client.search(index=self.index, body=search_body)
            hits = response['hits']['hits']
            
            devices = []
            for hit in hits:
                device = hit['_source']
                device['_id'] = hit['_id']
                devices.append(device)
                
            logger.debug(f"Found {len(devices)} vulnerable devices")
            return devices
            
        except exceptions.NotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error getting vulnerable devices: {e}")
            return []

    def bulk_index_devices(self, devices: List[Dict[str, Any]]) -> bool:
        """Bulk index multiple devices"""
        if not self.client:
            logger.error("OpenSearch client not available")
            return False
            
        try:
            operations = []
            for device in devices:
                operations.append({"index": {"_index": self.index}})
                operations.append(device)
            
            response = self.client.bulk(body=operations, refresh=True)
            
            if response.get('errors'):
                logger.error(f"Bulk indexing errors: {response}")
                return False
                
            logger.info(f"Bulk indexed {len(devices)} devices")
            return True
            
        except Exception as e:
            logger.error(f"Error in bulk indexing: {e}")
            return False

    def delete_index(self) -> bool:
        """Delete the index (for testing/cleanup)"""
        if not self.client:
            logger.error("OpenSearch client not available")
            return False
            
        try:
            if self.client.indices.exists(index=self.index):
                self.client.indices.delete(index=self.index)
                logger.info(f"Deleted index: {self.index}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False