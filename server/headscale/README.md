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

# Tagging a telescope

We need to add a tag 'telescope' to each TART telescope

    docker compose exec headscale headscale nodes list -t

This will give a list, something like

    ID | Hostname         | Name             | MachineKey | NodeKey | User           | IP addresses                   | Ephemeral | Last seen           | Expiration          | Connected | Expired | ForcedTags    | InvalidTags | ValidTags
    3  | vimes            | vimes            | [hPRdl]    | [yRCc0] | tart           | 100.64.0.3, fd7a:115c:a1e0::3  | false     | 2024-05-30 03:25:27 | 0001-01-01 00:00:00 | offline   | no      |               |             |          
    8  | client-example   | signal           | [S3f0y]    | [VP5E4] | tart           | 100.64.0.4, fd7a:115c:a1e0::4  | false     | 2024-05-31 00:18:28 | 0001-01-01 00:00:00 | offline   | no      |               |             |          
    9  | telescope-proxy  | telescope-proxy  | [kZmRQ]    | [aix9d] | tart           | 100.64.0.1, fd7a:115c:a1e0::1  | false     | 2025-07-26 02:45:26 | 0001-01-01 00:00:00 | online    | no      |               |             |          
    10 | tart3-test       | tart-kenya       | [Jc1FE]    | [//3Kd] | tart           | 100.64.0.2, fd7a:115c:a1e0::2  | false     | 2025-07-26 02:45:26 | 0001-01-01 00:00:00 | online    | no      | tag:telescope |             |          
    13 | za-rhodes        | za-rhodes        | [iMPX6]    | [qagrX] | tart           | 100.64.0.5, fd7a:115c:a1e0::5  | false     | 2025-07-26 02:45:26 | 0001-01-01 00:00:00 | online    | no      | tag:telescope |             |          
    14 | mu-udm           | mu-udm           | [e05Bb]    | [F0NcO] | tart           | 100.64.0.7, fd7a:115c:a1e0::7  | false     | 2025-07-26 02:47:11 | 0001-01-01 00:00:00 | online    | no      | tag:telescope |             |          

To tag a telescope, (in this case ID 14) use

    docker compose exec headscale headscale nodes tag --tags tag:telescope -i 14
