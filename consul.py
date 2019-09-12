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

    zones = []
    for key in resp.json():
        zone = key.split('/')[1]
        if zone not in zones:
            zones.append(zone)

    return zones
