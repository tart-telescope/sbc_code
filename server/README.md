# Server Side of the TART

The worldwide network of TART telescopes are all available directly, but also available through a common web interface at https://tart.elec.ac.nz/<tart_name>, where <tart_name> is the unique name of each TART. How this is done is described here.

* The cloud server runs a headscale server which creates the TART_VPN a virtual network..
* Each tart runs tailscale container that connects to the TART_VPN
* There is a service discovery running on the TART_VPN

<code>
TART_VPN: ----------------------------------------------------------------------------------------------------------
                             |                 |               |                    |
                          TART1               TART2          Discovery            HTTP
</code>

The role of the HTTP server is to make the TARTs available via the public internet. This is done using Caddy

## tart_vpn Network

This network lives inside docker. It is a headscale/tailscale VPN network hosted on cloud.elec.ac.nz.

    docker network create tart-vpn-nw
    
## TART proxy 

This server lives on the headscale network and matches http requests for example api.elec.ac.nz/tart/signal/{request} -> signal.tart.telescopes.elec.ac.nz/{request}
(https://caddyserver.com/docs/caddyfile/matchers#path)

    api.elec.ac.nz {
        @tartapi path_regexp tartapi /tart/([a-z]+)/*$
        reverse_proxy @tartapi http://{re.tartapi.tart}.tart.telescopes.elec.ac.nz/{re.tartapi.request}
    }

## HTTP Server

    caddy:
        image: caddy:latest
        container_name: caddy
        restart: always
        networks:
            tart-vpn-nw:
        stdin_open: true
        tty: true
        volumes:
            - ./container-data:/data
            - ./container-config:/config
            - /etc/localtime:/etc/localtime:ro
        ports:
            - 80:80
            - 443:443
        entrypoint: /usr/bin/caddy run --adapter caddyfile --config /config/Caddyfile

    networks:
    tart-vpn-nw:
        external: true

Where the /config
## Some links

* https://blog.gurucomputing.com.au/Reverse%20Proxies%20with%20Nginx%20Proxy%20Manager/Installing%20Nginx%20Proxy%20Manager/#routing-by-hostname


## Adding a TART

On the server, execute the following hich will generate an <AUTH_KEY>

    docker compose exec headscale \
        headscale --user myfirstuser preauthkeys create --reusable --expiration 24h

On the tart:

    docker exec tailscale \
        tailscale up --login-server <URL> --authkey <AUTH_KEY>
