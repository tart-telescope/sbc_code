# For development 

Use the docker-compose-dev.yml to bring up a local container and the web interface.

    docker compose -f docker-compose-dev.yml up --build

* API docs: http://localhost:8000/docs (admin / password)
* Web UI: http://localhost:8080
* Stop with `docker compose -f docker-compose-dev.yml down -v`

## Working on the web interface

The `ui` service builds the viewer from the sibling `web_app` checkout
(`../../web_app`) and tags it `tart-viewer:local`, so web-interface changes
show up in this environment with the same command as everything else:

    docker compose -f docker-compose-dev.yml up --build

To serve a published viewer image instead, set `VIEWER_IMAGE` (the build
section is then ignored):

    VIEWER_IMAGE=ghcr.io/tart-telescope/web_app/viewer-root:main \
      docker compose -f docker-compose-dev.yml up

## Seeing the corrupted calibration file error

The UI reports a corrupted or missing `calibrated_antenna_positions.json`
instead of spinning forever:

    cp calibrated_antenna_positions.json /tmp/positions.backup
    echo 'not json' > calibrated_antenna_positions.json
    docker compose -f docker-compose-dev.yml restart telescope-api

Open http://localhost:8080 to see the "Realtime view unavailable" banner with
the API's explanation. Restore the file and restart the API to clear it:

    cp /tmp/positions.backup calibrated_antenna_positions.json
    docker compose -f docker-compose-dev.yml restart telescope-api
