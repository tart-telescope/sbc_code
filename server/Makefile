COMPOSE=docker compose
USER=tart

network:
	docker network create reverseproxy-nw

build:
	${COMPOSE} build

up:
	${COMPOSE} up --remove-orphans
# check by pointing browser to http://localhost:9090/metrics

down:
	${COMPOSE} down

auth_key:
	${COMPOSE} exec headscale \
	        headscale --user ${USER} preauthkeys create --reusable --expiration 24h
	echo "make test_client AUTH_KEY=xxx"

test_client:
	${COMPOSE} -f test-client.yml exec tailscale \
		tailscale up --login-server http://dibbler:9080 --authkey ${AUTH_KEY}

# Run this only once...
namespace:
	${COMPOSE} exec headscale \
		headscale namespaces create ${USER}
