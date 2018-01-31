# Luzifer / dns

This repository contains the setup for my own DNS server. **You do not want to use the Repo as I'm maintaining it here!** (Why would you host my DNS for me?!?)

If you are looking at this because you're searching for inspiration:

- The Dockerfile contains a [CoreDNS](https://coredns.io/) server with added [alias plugin](https://coredns.io/explugins/alias/)
- In the configuration the `zones` folder is automatically added to the server
- The zone files are auto-formatted using [zonefmt](https://github.com/Luzifer/zonefmt)
