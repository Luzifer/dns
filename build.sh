#!/bin/bash
set -euxo pipefail

# Download sourcecode
mkdir -p /go/src/github.com/coredns
git clone https://github.com/coredns/coredns.git /go/src/github.com/coredns/coredns

# Ensure version pinning
cd /go/src/github.com/coredns/coredns
git reset --hard ${COREDNS_VERSION}

# Copy cron drop-in
cp /src/cron_generate.go .

# Get dependencies and build
go get -d -v
go install
