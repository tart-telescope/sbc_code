# sbc_code

Code for operating a TART, and providing the telescope RESTful API. This code runs on the embedded computer of the TART.


## Overview

The telescope software is built using docker software containers.
Some of the containers run on the telescope itself (the API and UI (web app), while others are used for calibration and providing a catalog of known objects.


* On the telescope itself, a Raspberry Pi (Model 3-5) which is plugged into the TART basestation board. This runs the telescope API and locale UI server.
* A calibration server which is a fast desktop or kubernetes cluster that runs a calibration routine at regular intervals (every few hours)
* A object position server. This is a server that provides a catalog of known objects and their elevation/azimuth for any point on earth. A public one is available so you'll only need to provide your own server if you're running a process that requires low-latency access to this information.
* A map service that provides detail of the deployed TARTs, their locations and status.
* A Web UI to view and control each TART remotely
* An S3 bucket that stores the visibility data for all TARTs
