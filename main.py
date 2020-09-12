#!/usr/bin/env python3

import argparse
import base64
import json
import sys
import urllib.request

with urllib.request.urlopen('https://v4.ident.me/') as f:
    ip = f.read().decode('utf-8')

with open('.env', 'r') as fh:
    env = dict(
        tuple(line.strip().split('=', 1))
        for line in fh.readlines() if not line.startswith('#') and line.strip()
    )

username = env['CPANEL_USERNAME']
password = base64.b64decode(env['CPANEL_PASSWORD']).decode()
address = env['CPANEL_ADDRESS']

domain = env['CPANEL_DOMAIN']
record_name = env['CPANEL_RECORD'].strip('.') + '.'

def req(params):
    url = f'https://{address}/json-api/cpanel?{urllib.parse.urlencode(params)}'
    auth = base64.b64encode(f'{username}:{password}'.encode()).decode()
    request = urllib.request.Request(url)
    request.add_header('Authorization', f'Basic {auth}')
    with urllib.request.urlopen(request) as f:
        return f.read().decode('utf-8')

query_params = {
    'cpanel_jsonapi_apiversion': '2',
    'cpanel_jsonapi_module': 'ZoneEdit',
    'cpanel_jsonapi_func': 'fetchzone_records',
    'domain': domain,
    'name': record_name,
}

records = json.loads(req(query_params))['cpanelresult']['data']

record = None
if len(records) > 0:
    if len(records) > 1:
        print('More than one record found for this domain.')
        sys.exit(1)

    record = records[0]
    if record['type'] != 'A':
        print('Existent record not of type A.')
        sys.exit(1)

edit_params = {
    'cpanel_jsonapi_apiversion': '2',
    'cpanel_jsonapi_module': 'ZoneEdit',
    'cpanel_jsonapi_func': 'edit_zone_record' if record else 'add_zone_record',
    'line': record['line'] if record else '0',
    'domain': domain,
    'name': record_name,
    'type': 'A',
    'address': ip,
    'ttl': '1800',
}
edit_response = json.loads(req(edit_params))
result = edit_response['cpanelresult']['data'][0]['result']

if result['status'] != 1:
    print(f'Error: {result["statusmsg"]}')
    sys.exit(1)

sys.exit(0)
