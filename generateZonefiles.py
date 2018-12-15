#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import hashlib
import os
import os.path
import sys
import time

# Custom modules
import consul

# Third-party imports
import dns.resolver
import dns.rdatatype
import jinja2
import requests
import yaml

DEFAULT_TTL = 3600


def default(d, key, default=None):
    if key in d:
        return d[key]
    return default


def diff_files(file1, file2):
    fromlines = []
    tolines = []
    if os.path.isfile(file1):
        with open(file1) as ff:
            fromlines = ff.readlines()
    if os.path.isfile(file2):
        with open(file2) as tf:
            tolines = tf.readlines()

    print(''.join(difflib.unified_diff(
        fromlines, tolines, file1, file2)))


def hash_file(filename):
    if not os.path.isfile(filename):
        return ""

    hasher = hashlib.sha1()
    with open(filename, 'r') as afile:
        lines = afile.readlines()

    lines = map(replace_soa_line, lines)

    hasher.update(''.join(lines).encode('utf-8'))
    return hasher.hexdigest()


def replace_soa_line(line):
    if 'SOA' in line:
        return '; SOA line replaced'
    return line


def resolve_alias(entry):
    result = []

    answers = []
    answers.extend(dns.resolver.query(
        entry['alias'], 'A', raise_on_no_answer=False))
    answers.extend(dns.resolver.query(
        entry['alias'], 'AAAA', raise_on_no_answer=False))

    if len(answers) == 0:
        raise Exception(
            "Alias {} was not resolvable: No answers!".format(entry['alias']))

    for rdata in answers:
        new_entry = entry.copy()
        del new_entry['alias']
        new_entry['type'] = dns.rdatatype.to_text(rdata.rdtype)
        new_entry['data'] = rdata.address
        result.append(new_entry)

    return sorted(result, key=lambda k: k['data'])


def sanitize(entry):
    result = []

    if entry['name'] == '':
        entry['name'] = '@'

    if 'alias' in entry:
        return resolve_alias(entry)

    for rr in entry['records']:
        new_entry = entry.copy()
        del new_entry['records']
        new_entry['data'] = rr

        if new_entry['type'] == 'TXT' and new_entry['data'][0] != '"':
            new_entry['data'] = '"{}"'.format(new_entry['data'])

        result.append(new_entry)

    result.sort(key=lambda k: k['data'])

    return result


def write_zone(zone, ttl, soa, nameserver, mailserver, entries):
    soa['serial'] = int(time.time()) - 946681200  # 2000-01-01

    tpl = jinja2.Template(open("zone_template.j2").read())
    zone_content = tpl.render({
        "zone": zone,
        "ttl": ttl,
        "soa": soa,
        "nameserver": nameserver,
        "mailserver": mailserver,
        "entries": entries,
    })

    with open("zones/tmp.{}".format(zone), 'w') as zf:
        zf.write(zone_content)

    if hash_file("zones/tmp.{}".format(zone)) != hash_file("zones/db.{}".format(zone)):
        print("Generated and replaced zone file for {}".format(zone))
        diff_files("zones/db.{}".format(zone), "zones/tmp.{}".format(zone))
        os.rename("zones/tmp.{}".format(zone), "zones/db.{}".format(zone))
    else:
        os.unlink("zones/tmp.{}".format(zone))


def healthcheck():
    if os.getenv('HC_PING') != '':
        requests.get(os.getenv('HC_PING'))


def main():
    zone_data = yaml.load(open("zones.yml"))

    consul_zones = consul.get_zones()
    zone_data['zones'] = {**consul_zones, **zone_data['zones']}

    for zone, config in zone_data['zones'].items():
        ttl = default(config, "default_ttl", DEFAULT_TTL)

        entries = []
        for entry in default(config, 'entries', []):
            entries.extend(sanitize(entry))

        if default(config, 'from_consul', False):
            for entry in consul.query_zone_entries(zone):
                entries.extend(sanitize(entry))

        mailserver = default(config, 'mailserver', {})
        if 'mailserver_set' in config and config['mailserver_set'] in zone_data['mailserver_sets']:
            mailserver = zone_data['mailserver_sets'][config['mailserver_set']]

        write_zone(zone, ttl, zone_data['soa'],
                   zone_data['nameserver'], mailserver, entries)

    healthcheck()


if __name__ == "__main__":
    main()
