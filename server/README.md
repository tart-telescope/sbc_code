# Server Side of the TART

Author: Tim Molteno (c) 2024

The worldwide network of TART telescopes are all available directly, but also available through a common web interface at https://tart.elec.ac.nz/<tart_name>, where <tart_name> is the unique name of each TART. How this is done is described here.

* The cloud server runs a headscale server which creates the TART_VPN a virtual network..
* Each tart runs tailscale container that connects to the TART_VPN
* There is a special proxy running on the TART_VPN that provides access to each TART.

<code>
TART_VPN: ----------------------------------------------------------------------------------------------------------
                             |                 |               |                    |
                          TART1              TART2           Proxy                TART3
</code>

The role of the HTTP server is to make the TARTs available via the public internet. This is done using Caddy

    
## TART proxy 

See the proxy directory... If a TART is called <tart_name> then it will be visible at

    https://api.elec.ac.nz/tart/<tart_name>/
    
and it's API endpoint will be 

    https://api.elec.ac.nz/tart/<tart_name>/api

and it's API documentation will be available at 

    https://api.elec.ac.nz/tart/<tart_name>/doc

## Adding a TART

The first time a TART is configured and run (see ../software) it will need to be given a unique tart name, and then
authenticated onto the cloud by a system administrator.

	ssh tart@cloud.elec.ac.nz \
		'cd headscale; docker compose exec headscale \
	        headscale -o yaml --user tart preauthkeys create --reusable --expiration 24h | grep key'

	docker compose exec tailscale tailscale up --hostname=nz-dunedin --login-server http://cloud.elec.ac.nz --authkey=

