import base64
import json
import os
import requests


def get_zones():
    if os.getenv('CONSUL_HTTP_ADDR') == '' or os.getenv('CONSUL_HTTP_TOKEN') == '':
        raise Exception(
            'Consul query does not work with CONSUL_HTTP_ADDR or CONSUL_HTTP_TOKEN unset')

    resp = requests.get(
        '{}/v1/kv/dns?keys=true'.format(
            os.getenv('CONSUL_HTTP_ADDR'),
        ),
        headers={
            'X-Consul-Token': os.getenv('CONSUL_HTTP_TOKEN'),
        }
    )

    if resp.status_code == 404:
        return []

    zones = {}
    for key in resp.json():
        zone = key.split('/')[1]
        if zone not in zones:
            zones[zone] = {'from_consul': True}

    return zones


def query_zone_entries(zone):
    if os.getenv('CONSUL_HTTP_ADDR') == '' or os.getenv('CONSUL_HTTP_TOKEN') == '':
        raise Exception(
            'Consul query does not work with CONSUL_HTTP_ADDR or CONSUL_HTTP_TOKEN unset')

    return parse_raw_consul(zone)


def read_raw_from_consul(zone):
    resp = requests.get(
        '{}/v1/kv/dns/{}?recurse=true'.format(
            os.getenv('CONSUL_HTTP_ADDR'),
            zone.rstrip('.'),
        ),
        headers={
            'X-Consul-Token': os.getenv('CONSUL_HTTP_TOKEN'),
        }
    )

    if resp.status_code == 404:
        return []

    return resp.json()


def parse_raw_consul(zone):
    entries = []

    for raw_entry in read_raw_from_consul(zone):
        sub_entries = json.loads(base64.b64decode(raw_entry['Value']))

        # Key consists of at least 2 elements: dns/ahlers.me/subdomain OR dns/ahlers.me
        key = raw_entry['Key'].split('/')[2:]
        name = ''
        if len(key) > 0 and key[0] != '@':
            name = key[0]

        for entry in sub_entries:
            entry['name'] = name
            entries.append(entry)

    return entries
