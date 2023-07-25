# Server Side of the TART

The worldwide network of TART telescopes are all available directly, but also available through a common web interface at http://tart.elec.ac.nz/<tart_name>, where <tart_name> is the unique name of each TART. How this is done is described here.


## Service Discovery

Each TART telescope runs a service that connects it to a VPN network hosted in the cloud. This is done by using headscale on tart.elec.ac.nz. 
This tailscale exists on a docker network

    docker network create reverseproxy-nw


Change to your hostname or host IP (https://github.com/juanfont/headscale/blob/main/docs/reverse-proxy.md)

    service: headscale
        image: headscale:latest
        volume $(pwd)/config:/etc/headscale/ \
        ports:
            8080:8080
            9090:9090

    service: caddy
        caddyfile:   
        tart.elec.ac.nz {
            reverse_proxy headscale:8080
        }

    services:
    caddy:
        image: caddy:latest
        container_name: caddy
        restart: always
        networks:
            reverseproxy-nw:
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
    reverseproxy-nw:
        external: true
## Adding a TART

On the server, execute the following hich will generate an <AUTH_KEY>

    docker compose exec headscale \
        headscale --user myfirstuser preauthkeys create --reusable --expiration 24h

On the tart:

    docker exec tailscale \
        tailscale up --login-server <URL> --authkey <AUTH_KEY>
