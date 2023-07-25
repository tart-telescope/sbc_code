COMPOSE="docker compose"

build:
	${COMPOSE} build

up:
	${COMPOSE} up --remove-orphans

down:
	${COMPOSE} down

auth_client:
	${COMPOSE} -f test-client.yml exec tailscale \
		tailscale up --login-server http://dibbler:9080 --authkey ${AUTH_KEY}
