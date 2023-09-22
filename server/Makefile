COMPOSE=docker compose -f docker-compose.yml
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


api_key:
	${COMPOSE} exec headscale \
	        headscale apikeys create

# Run this only once...
namespace:
	${COMPOSE} exec headscale \
		headscale namespaces create ${USER}

# headscale nodes register --user tart --key nodekey:0e985c452bded096544c2bf27d4043d0643912a3726397f21ce39015d5b26a1f
# headscale nodes register --user tart --key nodekey:54fe44e10fd3722d2090df86f9ad91e54ea1b129ee5c084a1d9dfd9826052a06
