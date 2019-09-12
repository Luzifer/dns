#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import hashlib
import os
import os.path
import subprocess
import sys
import time

# Custom modules
import consul

# Third-party imports
import jinja2
import requests
import yaml


rndc_queue = []


def call_rndc(params):
    command = ["rndc"]
    command.extend(params)

    if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'true':
        print('DBG: Call "{}"'.format(" ".join(command)))
    else:
        subprocess.check_call(command, stdout=sys.stdout, stderr=sys.stderr)


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


def exec_rndc_queue():
    global rndc_queue

    for params in rndc_queue:
        call_rndc(params)

    rndc_queue = []


def hash_file(filename):
    if not os.path.isfile(filename):
        return ""

    hasher = hashlib.sha1()
    with open(filename, 'r') as afile:
        lines = afile.readlines()

    hasher.update(''.join(lines).encode('utf-8'))
    return hasher.hexdigest()


def queue_rndc_call(params):
    global rndc_queue

    rndc_queue.append(params)


def write_named_conf(zones):
    tpl = jinja2.Template(open("named.conf").read())
    zone_content = tpl.render({
        "zones": zones,
    })

    with open("zones/named.conf.new", "w") as f:
        f.write(zone_content)

    if hash_file("zones/named.conf.new") != hash_file("zones/named.conf"):
        print("Generated and replaced named.conf")
        diff_files("zones/named.conf", "zones/named.conf.new")
        os.rename("zones/named.conf.new", "zones/named.conf")

        queue_rndc_call(['reconfig'])
    else:
        os.unlink("zones/named.conf.new")


def healthcheck():
    if os.getenv('HC_PING') is not None:
        requests.get(os.getenv('HC_PING'))


def main():
    consul_zones = consul.get_zones()
    write_named_conf(consul_zones)

    exec_rndc_queue()

    healthcheck()


if __name__ == "__main__":
    main()
