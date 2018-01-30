#!/bin/bash
set -euxo pipefail

IFS=$'\n'

GOPKGS=(
  'github.com/coredns/coredns'
  'github.com/Luzifer/alias'
)

for pkg in ${GOPKGS[@]}; do
  go get -d -v "${pkg}"
done

PLUGINS=(
  '/^file:file/ i alias:github.com/Luzifer/alias'
)

cd /go/src/github.com/coredns/coredns
for insert in ${PLUGINS[@]}; do
  sed -i "${insert}" plugin.cfg
done

go generate
go install
