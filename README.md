# Luzifer / dns

This repository contains the setup for my own DNS server. **You do not want to use the Repo as I'm maintaining it here!** (Why would you host my DNS for me?!?)

If you are looking at this because you're searching for inspiration:

- The Dockerfile contains a [CoreDNS](https://coredns.io/) server with added cron to generate zone files on the fly
- The auto-generator supports fake-alias records by running every minute fetching the latest A/AAAA records for the aliased domain
- There is a check script which looks for obvious errors in the `zones.yml` file
