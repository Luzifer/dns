#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Third-party imports
import dns.resolver
import dns.rdatatype
import jinja2
import yaml

DEFAULT_TTL = 3600


def default(d, key, default=None):
    if key in d:
        return d[key]
    return default


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

    return result


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

    return result


def write_zone(zone, ttl, soa, nameserver, mailserver, entries):
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

    # FIXME (kahlers): Check if contents changed
    os.rename("zones/tmp.{}".format(zone), "zones/db.{}".format(zone))


def main():
    zone_data = yaml.load(open("zones.yml"))

    for zone, config in zone_data['zones'].items():
        ttl = default(config, "default_ttl", DEFAULT_TTL)

        entries = []
        for entry in config['entries']:
            entries.extend(sanitize(entry))

        write_zone(zone, ttl, zone_data['soa'],
                   zone_data['nameserver'], default(config, 'mailserver', {}), entries)


if __name__ == "__main__":
    main()
