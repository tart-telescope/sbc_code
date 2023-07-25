network:
	docker network create reverseproxy-nw

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

new_tart:
	docker compose exec headscale \
	        headscale -n tartnamespace preauthkeys create --reusable --expiration 24h

test_client:
	docker exec tailscale \
		tailscale up --login-server http://172.16.1.108:9080 --authkey ${AUTH_KEY}

# Run this only once...
namespace:
	docker compose exec headscale \
		headscale namespaces create tartnamespace

