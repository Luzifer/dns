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

# Force downgrades not being pinned
CWD=$(pwd)
cd ${GOPATH}/src/github.com/mholt/caddy              && git checkout -q v0.10.10
cd ${GOPATH}/src/github.com/miekg/dns                && git checkout -q v1.0.4
cd ${GOPATH}/src/github.com/prometheus/client_golang && git checkout -q v0.8.0
cd ${GOPATH}/src/golang.org/x/net                    && git checkout -q release-branch.go1.9
cd ${GOPATH}/src/golang.org/x/text                   && git checkout -q e19ae1496984b1c655b8044a65c0300a3c878dd3
cd "${CWD}"

# Do the compile
go install
