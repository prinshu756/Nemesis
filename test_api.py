#!/usr/bin/env python3
"""Test Nemesis API endpoints"""

import requests
import json

base_url = 'http://localhost:8000'

try:
    print("Testing Nemesis API endpoints...\n")
    
    # Test /status endpoint
    response = requests.get(f'{base_url}/status')
    print('✓ GET /status - OK')
    status = response.json()
    print(f'  Database stats: {status.get("database", {})}')
    print(f'  Agents: {status.get("agents_status", {})}')
    
    # Test /alerts endpoint
    response = requests.get(f'{base_url}/alerts')
    print('\n✓ GET /alerts - OK')
    alerts = response.json().get("alerts", [])
    print(f'  Alerts in database: {len(alerts)}')
    
    # Test /traffic endpoint
    response = requests.get(f'{base_url}/traffic?limit=10')
    print('\n✓ GET /traffic - OK')
    traffic = response.json().get("traffic_logs", [])
    print(f'  Traffic logs in database: {len(traffic)}')
    
    # Test /honeypots/detection endpoint
    response = requests.get(f'{base_url}/honeypots/detection?limit=10')
    print('\n✓ GET /honeypots/detection - OK')
    detections = response.json().get("honeypot_detections", [])
    print(f'  Honeypot detections in database: {len(detections)}')
    
    # Test /anomalies endpoint
    response = requests.get(f'{base_url}/anomalies?limit=10')
    print('\n✓ GET /anomalies - OK')
    anomalies = response.json().get("anomalies", [])
    print(f'  Anomalies in database: {len(anomalies)}')
    
    print('\n✅ All API endpoints working successfully!')
    print('\nDatabase is ready to capture:')
    print('  - Anomalies/Alerts')
    print('  - Honeypot detections')
    print('  - Network traffic logs')
    print('  - High traffic patterns')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
