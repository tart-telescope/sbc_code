COMPOSE=docker compose -f docker-compose.yml
USER=tart

build:
	docker compose  --progress=plain --parallel=1 build
auth:
	ssh tart@cloud.elec.ac.nz \
		'cd headscale; docker compose exec headscale \
	        headscale -o yaml --user ${USER} preauthkeys create --reusable --expiration 24h | grep key'
	@echo "docker compose exec tailscale tailscale up --hostname=telescopeproxy --login-server http://cloud.elec.ac.nz --authkey=..."
