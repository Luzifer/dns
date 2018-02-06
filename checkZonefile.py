#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import generateZonefiles as generator

import re
import sys
import yaml

MATCH_FQDN = '(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}.$)'

result_code = 0


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def error(msg):
    global result_code
    print(bcolors.FAIL + "[ERR] {}".format(msg) + bcolors.ENDC)
    result_code = 1


def fatal(msg):
    print(bcolors.FAIL + '[FAT] {}'.format(msg) + bcolors.ENDC)
    sys.exit(1)


def warn(msg):
    print(bcolors.WARNING + "[WRN] {}".format(msg) + bcolors.ENDC)


def check_entry(zone_name, entry):
    optional_entry = ['name', 'type', 'ttl', 'class', 'records', 'alias']

    if 'name' not in entry:
        error('Zone "{}" contains entry without name'.format(zone_name))
        return

    if 'alias' not in entry and 'records' not in entry:
        error('Zone "{}" - Entry "{}" - Neither alias nor records specified'.format(
              zone_name, entry['name']))
        return

    for k in entry.keys():
        if k not in optional_entry:
            warn('Zone "{}" - Entry "{}" - Unexpected key in entry found: {}'.format(
                zone_name, entry['name'], k))

    parsed_entries = generator.sanitize(entry)

    if len(parsed_entries) == 0:
        warn('Zone "{}" - Entry "{}" - Resolved to 0 resource records!'.format(
            zone_name, entry['name']))

    # TODO(kahlers): Add more checks:
    # - Type is valid
    # - Class is valid


def check_soa(soa, nameservers):
    # SOA check
    expected_soa = ['auth_ns', 'contact', 'refresh', 'retry', 'expire', 'ttl']
    for e in expected_soa:
        if e not in soa:
            fatal('Missing required attribute {} in soa'.format(e))

    for k in soa.keys():
        if k not in expected_soa:
            warn('Unexpected entry in soa found: {}'.format(k))

    if soa['auth_ns'] not in nameservers:
        error('SOA auth nameserver not in nameserver list')

    if not re.match("^[a-z.]+.$", soa['contact']):
        error('SOA contact does not match specificiation')

    if not 1200 <= soa['refresh'] <= 43200:
        warn('SOA refresh out of recommended bounds 1200 - 43200')

    if not 180 <= soa['retry'] <= 900:
        warn('SOA retry out of suggested bounds 180 - 900')

    if not 1209600 <= soa['expire'] <= 2419200:
        warn('SOA expire out of recommended bounds 1209600 - 2419200')

    if not 300 <= soa['ttl'] <= 86400:
        warn('SOA minimum ttl out of recommended bounds 300 - 86400')


def check_nameserver(nameservers):
    if len(nameservers) < 2:
        error('Number of nameservers below required 2 servers')

    if not 3 <= len(nameservers) <= 7:
        warn('Number of nameservers out of recommended bounds 3 - 7 (RFC2182)')

    for n in nameservers:
        if not re.match(MATCH_FQDN, n):
            warn('Nameserver {} does not match fqdn regexp'.format(n))

    # TODO(kahlers): Add more checks:
    # - Nameservers do not have same IP
    # - Nameservers are reachable
    # - Nameservers are not in same AS


def check_zone(name, config):
    expected_zone = ['mailserver', 'entries']

    for k in config.keys():
        if k not in expected_zone:
            warn('Unexpected entry in zone {} found: {}'.format(name, k))

    if 'mailserver' not in config and ('entries' not in config or len(config['entries']) == 0):
        warn('Zone {} has no mailservers and no entries'.format(name))

    if 'mailserver' in config:
        for mx, weight in config['mailserver'].items():
            if not str(weight).isdigit():
                error('Zone {} - MX entry {} has non-digit weight {}'.format(
                    name, mx, weight))

            if not re.match(MATCH_FQDN, mx):
                warn('Zone {} - MX {} does not match fqdn regexp'.format(name, mx))

    if 'entries' in config:
        for e in config['entries']:
            check_entry(name, e)


def main():
    zone_data = yaml.load(open("zones.yml"))

    if 'soa' not in zone_data:
        fatal("SOA configuration not found")

    if 'nameserver' not in zone_data:
        fatal("Nameserver list not found")

    if 'zones' not in zone_data:
        error('No zones configuration found')

    check_soa(zone_data['soa'], zone_data['nameserver'])
    check_nameserver(zone_data['nameserver'])

    for name, config in zone_data['zones'].items():
        check_zone(name, config)

    return result_code


if __name__ == "__main__":
    sys.exit(main())
