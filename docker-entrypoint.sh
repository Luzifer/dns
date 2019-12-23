#!/usr/local/bin/dumb-init /bin/bash
set -euxo pipefail

# Ensure default config without zones
[ -e /src/zones/named.conf ] || {
	cp /src/named.conf.default /src/zones/named.conf
}

if [ "${1:-}" = 'named' ]; then
	# Generate rndc communication key
	rndc-confgen -a
	chmod 0644 /etc/bind/rndc.key

	# Start crond in the background
	crond

	# Start coredns
	exec "$@"
fi

exec "$@"
