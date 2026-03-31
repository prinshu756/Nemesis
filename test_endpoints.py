"""Quick endpoint validation script for N.E.M.E.S.I.S API."""
import urllib.request, json, sys

BASE = 'http://localhost:8000'
results = []

endpoints = [
    ('/', 'Root'),
    ('/status', 'System Status'),
    ('/devices', 'Devices'),
    ('/alerts', 'Alerts'),
    ('/network-map', 'Network Map'),
    ('/logs', 'Logs'),
    ('/threats', 'Threats'),
    ('/honeypots', 'Honeypots'),
    ('/agents/status', 'Agent Status'),
    ('/metrics', 'Metrics'),
]

print("=" * 50)
print("  N.E.M.E.S.I.S API ENDPOINT VALIDATION")
print("=" * 50)

for path, name in endpoints:
    try:
        r = urllib.request.urlopen(BASE + path, timeout=5)
        d = json.loads(r.read())
        
        info = ""
        if path == '/':
            info = f"v{d.get('version','?')} - {d.get('status','?')}"
        elif path == '/status':
            info = f"state={d.get('system_state','?')} devices={d.get('devices',{}).get('total',0)} cycles={d.get('cycles',0)}"
        elif path == '/devices':
            info = f"{d.get('count',0)} devices"
        elif path == '/alerts':
            info = f"{d.get('count',0)} alerts" 
        elif path == '/network-map':
            info = f"{len(d.get('devices',[]))} nodes, {len(d.get('connections',[]))} links"
        elif path == '/logs':
            info = f"{d.get('count',0)} log entries"
        elif path == '/threats':
            info = f"{d.get('active_count',0)} active, {d.get('total_count',0)} total"
        elif path == '/honeypots':
            info = f"{d.get('active',0)} active, {d.get('total',0)} total"
        elif path == '/agents/status':
            info = f"A:{d['alpha']['status']} B:{d['beta']['status']} G:{d['gamma']['status']}"
        elif path == '/metrics':
            info = f"CPU:{d.get('cpu_usage','?')}% MEM:{d.get('memory_used','?')}%"
        
        print(f"  [PASS] {name:20s} {path:20s} {info}")
        results.append(True)
    except Exception as e:
        print(f"  [FAIL] {name:20s} {path:20s} {str(e)[:50]}")
        results.append(False)

print("=" * 50)
passed = sum(results)
total = len(results)
print(f"  Result: {passed}/{total} endpoints passed")
if passed == total:
    print("  ALL ENDPOINTS OPERATIONAL")
else:
    print(f"  {total - passed} ENDPOINTS FAILED")
print("=" * 50)
