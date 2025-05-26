DOCKER=/usr/bin/docker
COMPOSE=/usr/bin/docker compose --progress plain
USER=tart

build:
	${COMPOSE} --parallel 1  build

up:
	${COMPOSE} up -d

down:
	${COMPOSE} down

logs:
	${COMPOSE} logs -f

TART=tart@nz-dunedin
install:
	rsync --recursive --verbose \
			--exclude '*.venv*' \
			--exclude '.env'  \
			--exclude 'node_modules'  \
			--exclude '*config_data/*.json'  \
			--exclude '*.egg-info' \
			--exclude '*.bak' \
			--exclude '*.pyc' . ${TART}:code/

update:
	rsync --recursive --verbose \
			--exclude '*.venv*' \
			--exclude 'telescope_config/*'
			--exclude '.env'  \
			--exclude 'node_modules'  \
			--exclude '*config_data/*.json'  \
			--exclude '*.egg-info' \
			--exclude '*.bak' \
			--exclude '*.pyc' . ${TART}:code/
