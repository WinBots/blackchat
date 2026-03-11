import subprocess
import time
import http.client
import json

cmd = [
    'python',
    '-m',
    'uvicorn',
    'app.main:app',
    '--host',
    '127.0.0.1',
    '--port',
    '8062'
]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    time.sleep(2)
    conn = http.client.HTTPConnection('127.0.0.1', 8062)
    payload = json.dumps({'config': {'nodePositions': {}, 'connections': []}})
    headers = {'Content-Type': 'application/json'}
    conn.request('PUT', '/api/v1/flows/8', payload, headers)
    response = conn.getresponse()
    print('status', response.status)
    print(response.read().decode())
    conn.close()
finally:
    proc.terminate()
    time.sleep(1)
    out, _ = proc.communicate()
    print('=== SERVER LOG ===')
    print(out)
