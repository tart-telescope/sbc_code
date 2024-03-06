COMPOSE=docker compose -f docker-compose.yml
USER=tart

auth:
	ssh tart@cloud.elec.ac.nz \
		'cd headscale/server; docker compose exec headscale \
	        headscale -o yaml --user ${USER} preauthkeys create --reusable --expiration 24h | grep key:'
	@echo "docker compose exec tailscale tailscale up --login-server http://cloud.elec.ac.nz:51820 --authkey=..."
