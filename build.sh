#!/bin/bash
set -euxo pipefail

# Install build utilities
apk --no-cache add curl

# Install dependencies
apk --no-cache add python3 bind-tools

# Get latest versions of tools using latestver
COREDNS_VERSION=$(curl -sSfL 'https://lv.luzifer.io/catalog-api/coredns/latest.txt?p=version')
DUMB_INIT_VERSION=$(curl -sSfL 'https://lv.luzifer.io/catalog-api/dumb-init/latest.txt?p=version')

[ -z "${COREDNS_VERSION}" ] && { exit 1; }
[ -z "${DUMB_INIT_VERSION}" ] && { exit 1; }

# Install tools
curl -sSfL https://github.com/coredns/coredns/releases/download/v${COREDNS_VERSION}/coredns_${COREDNS_VERSION}_linux_amd64.tgz | \
  tar -x -z -C /usr/local/bin

curl -sSfLo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_amd64
chmod +x /usr/local/bin/dumb-init

# Install requirements for python3 scripts
pip3 install -r /src/requirements.txt

# Create cron to update zones periodically
echo "*       *       *       *       *       run-parts /etc/periodic/1min" >> /var/spool/cron/crontabs/root
mkdir -p /etc/periodic/1min
ln -s /src/zonefile_cron /etc/periodic/1min/zonefile_cron

# Cleanup
apk --no-cache del curl
