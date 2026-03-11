import http.client
import json

conn = http.client.HTTPConnection('127.0.0.1', 8061)
payload = json.dumps({
    'config': {
        'nodePositions': {},
        'connections': []
    }
})
headers = {'Content-Type': 'application/json'}
conn.request('PUT', '/api/v1/flows/8', payload, headers)
res = conn.getresponse()
print('status', res.status)
print(res.read().decode())
