DOCKER=/usr/bin/docker
COMPOSE="/usr/bin/docker compose --progress plain"
USER=tart

build:
	${COMPOSE} --parallel 1 -f docker-compose-test.yml build

up:
	${COMPOSE} -f docker-compose-test.yml up -d

down:
	${COMPOSE} -f docker-compose-test.yml down
