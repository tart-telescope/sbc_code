COMPOSE=docker compose

build:
	${COMPOSE} build

up:
	${COMPOSE} up --remove-orphans

down:
	${COMPOSE} down

auth_client:
	${COMPOSE} exec tailscale \
		tailscale up --login-server http://tart.elec.ac.nz:51820 --hostname=rhodes
		#--authkey ${AUTH_KEY}
