COMPOSE="docker compose"
USER=tart

build:
	${COMPOSE} --progress plain --parallel 1 -f docker-compose-test.yml build

up:
	${COMPOSE} -f docker-compose-test.yml up -d

down:
	${COMPOSE} -f docker-compose-test.yml down
