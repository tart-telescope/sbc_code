# Configuration for the headscale VPN

The headscale network has a domain name of telescope.network. This means that if a host called 'signal' connects to this network,
it will have a domain name of signal.tart.telescopes.elec.ac.nz


## Headscale

To issue commands for headscale

    docker compose exec headscale /bin/bash

## Add a telescope

Create a new device key for user 'tart'. Then authenticate the user during bring up on the TART telescope.

## Proxy

A single host sits on the headscale network and acts as a proxy routing /user/host to the correct internal domain name. This is just another machine on the tailscale network. At this stage the proxy is configured manually.

## GUI

There is a basic gui that requires API keys to work. https://cloud.elec.ac.nz/web/users.html. 

    docker compose exec headscale headscale apikeys list
