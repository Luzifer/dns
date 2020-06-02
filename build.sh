#!/bin/bash
set -euxo pipefail

# Install build utilities
apk --no-cache add curl

# Install dependencies
apk --no-cache add \
	bind \
	bind-tools \
	py3-pip \
	python3

# Get latest versions of tools using latestver
DUMB_INIT_VERSION=$(curl -sSfL 'https://lv.luzifer.io/catalog-api/dumb-init/latest.txt?p=version')

[ -z "${DUMB_INIT_VERSION}" ] && { exit 1; }

# Install tools
curl -sSfLo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_amd64
chmod +x /usr/local/bin/dumb-init

# Install requirements for python3 scripts
pip3 install -r /src/requirements.txt

# Create cron to update zones periodically
echo "*       *       *       *       *       run-parts /etc/periodic/1min" >>/var/spool/cron/crontabs/root
mkdir -p /etc/periodic/1min
ln -s /src/zonefile_cron /etc/periodic/1min/zonefile_cron

# Link named.conf
ln -sf /src/zones/named.conf /etc/bind/named.conf

# Cleanup
apk --no-cache del curl
