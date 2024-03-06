COMPOSE=docker compose

build:
	${COMPOSE} build

up:
	${COMPOSE} up --remove-orphans

down:
	${COMPOSE} down

auth_client:
	${COMPOSE} exec tailscale \
		tailscale up --login-server https://cloud.elec.ac.nz --hostname=rhodes
		#--authkey ${AUTH_KEY}
