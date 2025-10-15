import shodan
import time
import logging
from typing import List, Dict, Any
import random
from .opensearch import OpenSearchHelper

logger = logging.getLogger(__name__)

def ingest_shodan_sample_safe(es: OpenSearchHelper) -> int:
    """Safely ingest sample Shodan data"""
    try:
        sample_devices = generate_sample_devices(20)
        success = es.bulk_index_devices(sample_devices)
        return len(sample_devices) if success else 0
    except Exception as e:
        logger.error(f"Error in sample ingestion: {e}")
        return 0

def ingest_shodan_query_safe(es: OpenSearchHelper, query: str, api_key: str) -> int:
    """Safely ingest Shodan data using query"""
    try:
        api = shodan.Shodan(api_key)
        results = api.search(query)
        
        devices = []
        for result in results['matches'][:50]:  # Limit to 50 results
            device = {
                'ip': result['ip_str'],
                'port': result['port'],
                'hostname': result.get('hostnames', [''])[0],
                'service': result.get('product', 'Unknown'),
                'status': 'online',
                'data': result.get('data', ''),
                'timestamp': time.time() * 1000,
                'vulnerabilities': []
            }
            
            # Add location if available
            if 'location' in result:
                device['location'] = {
                    'lat': result['location']['latitude'],
                    'lon': result['location']['longitude']
                }
            
            devices.append(device)
        
        success = es.bulk_index_devices(devices)
        return len(devices) if success else 0
        
    except shodan.APIError as e:
        logger.error(f"Shodan API error: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error in Shodan query ingestion: {e}")
        return 0

def generate_sample_devices(count: int = 20) -> List[Dict[str, Any]]:
    """Generate sample device data for testing"""
    sample_ips = [
        "192.168.1.100", "192.168.1.101", "192.168.1.102", "192.168.1.103",
        "10.0.0.50", "10.0.0.51", "10.0.0.52", "172.16.0.100", "172.16.0.101"
    ]
    
    services = ["CCTV Camera", "Webcam", "DVR", "NVR", "IP Camera", "Security Camera"]
    locations = [
        {"lat": 37.7749, "lon": -122.4194},  # San Francisco
        {"lat": 40.7128, "lon": -74.0060},   # New York
        {"lat": 51.5074, "lon": -0.1278},    # London
        {"lat": 35.6762, "lon": 139.6503},   # Tokyo
        {"lat": 48.8566, "lon": 2.3522}      # Paris
    ]
    
    devices = []
    for i in range(count):
        ip = random.choice(sample_ips) if i < len(sample_ips) else f"192.168.1.{100 + i}"
        
        device = {
            'ip': ip,
            'hostname': f'camera-{i+1}.local',
            'service': random.choice(services),
            'port': random.choice([80, 443, 554, 8080]),
            'status': random.choice(['online', 'online', 'online', 'offline']),
            'location': random.choice(locations),
            'last_seen': f"2024-01-{15 + (i % 10):02d}T{10 + (i % 8):02d}:00:00Z",
            'timestamp': time.time() * 1000 - (i * 3600000),  # Stagger timestamps
            'vulnerabilities': []
        }
        
        # Add some vulnerabilities
        if random.random() < 0.3:  # 30% chance of vulnerabilities
            device['vulnerabilities'] = [
                {
                    'cve_id': f"CVE-2024-{1000 + i}",
                    'description': 'Default credentials vulnerability',
                    'cvss_score': round(random.uniform(5.0, 9.0), 1),
                    'type': 'authentication'
                }
            ]
        
        devices.append(device)
    
    return devices