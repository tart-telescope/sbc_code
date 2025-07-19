## TART Docker Files

This directory contains Dockerfiles that automate the execution of the parts of the telescope. These are

Author: Tim Molteno (tim@elec.ac.nz)

### Web Application (ui)

This is a containerized javascript application served by a web server on the raspberry pi that runs in a browser and communicates with the Telescope API to view the telescope.
This docker image should be installed on the raspberry pi with the telescope hardware and/or on a remote server.

### Telescope API (telescope_api)

This allows remote control of the telescope via a Restful interface. The web front end uses this API to configure and get data from the telescope.
This docker image should be installed on the raspberry pi with the telescope hardware.
