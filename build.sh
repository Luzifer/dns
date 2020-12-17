#!/bin/bash
set -euxo pipefail

# Install build utilities
apk --no-cache add curl jq

# Install dependencies
apk --no-cache add \
	bind \
	bind-tools \
	py3-pip \
	python3

# Get latest versions of tools using Github API
ASSET_URL=$(
	curl -s "https://api.github.com/repos/Yelp/dumb-init/releases/latest" |
		jq -r '.assets[] | .browser_download_url' |
		grep "$(uname -m)$"
)
[[ -n $ASSET_URL ]] || exit 1

# Install tools
curl -sSfLo /usr/local/bin/dumb-init "${ASSET_URL}"
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
apk --no-cache del curl jq
