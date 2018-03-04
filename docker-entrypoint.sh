#!/usr/local/bin/dumb-init /bin/bash
set -euxo pipefail

if [ "${1:-}" = 'coredns' ]; then
  # Start crond in the background
  crond

  # Start coredns
  exec "$@"
fi

exec "$@"
