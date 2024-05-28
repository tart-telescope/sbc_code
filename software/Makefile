DOCKER=/usr/bin/docker
COMPOSE=/usr/bin/docker compose --progress plain
USER=tart

build:
	${COMPOSE} --parallel 1 -f docker-compose-test.yml build

up:
	${COMPOSE} -f docker-compose-test.yml up -d

down:
	${COMPOSE} -f docker-compose-test.yml down

logs:
	${COMPOSE} -f docker-compose-test.yml logs -f

TART=tart@nzdunedin
install:
	rsync --recursive --verbose --exclude '*.venv*'  --exclude 'node_modules'  --exclude '*.egg-info' --exclude '*.bak' --exclude '*.pyc' . ${TART}:code/
