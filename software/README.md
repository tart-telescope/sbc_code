## TART Software


## Local Site Configuration

You can copy and modify the files in `software/telescope_config.json` and `software/calibrated_antenna_positions.json`
to contain the new telescopes' configuration information (latitude, longitude, altitude) as well as the calibrated antenna positions.
We will need these later.


## Installation on a target Raspberry Pi

The following procedure will install all the necessary TART software on a Raspberry Pi (Model 3 or later) attached to the TART hardware.

### Step 1. Prepare the Pi

Download latest Raspberry Pi OS Lite image from https://www.raspberrypi.org/software/operating-systems/
Download Etcher from https://www.balena.io/etcher/ and flash the Image onto a SD Card.
This will take a couple of minutes... When done insert the sd card into raspberry pi and wait for it to boot up.
Create an empty file called ssh and copy it onto the sd card (Make sure that the ssh file has no file extention)

Log in or SSH into the Raspberry Pi
   user: tart
    pw: <xxxxxxx>

```bash
    ssh tart@pi.local
```

Set hostname to something suitable we'll use 'nz-elec',
```bash
    sudo hostnamectl hostname nz-elec
```
activate SPI & SSH with raspi-config ( SSH and SPI can be enabled under Interfacing Options) :
```bash
    sudo raspi-config
    sudo apt update
    sudo apt dist-upgrade
```
Install tailscale on the TART
```bash
    curl -fsSL https://tailscale.com/install.sh | sh
```
Now set up tailscale onto the elec.ac.nz tailcale network. This is done using
```bash
    sudo tailscale up
```
Ensure that key expiry is disabled for this machine.

Install docker on the SBC. This is done by following commands.
```bash
    curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo reboot
```
### Prepare the pi for long-term use

Add tempfs for /var/log (https://github.com/azlux/log2ram)
Fix up journald (https://forums.raspberrypi.com/viewtopic.php?t=341605)

### Step 2. Copy code to the Pi
```bash
    make install TART=user@tart-host
```
### Step 3. Configuration on the Pi

SSH into the raspberry pi after completing step 1.
```bash
    cd code
```
Use openssl to generate a secret key
```bash
    openssl rand -base64 24
```
Create a secrets file called .env with the variables
```bash
TS_HOSTNAME=my-hostname
LOGIN_PW=xxx
SECRET_KEY=your-secret-key-xxx
```

- `${TS_HOSTNAME}`
    - e.g. nz-elec
    - will be the public name of the TART telescope https://tart.elec.ac.nz/viewer/`${TS_HOSTNAME}`
    - defines the API endpoint of the TART telescope https://api.elec.ac.nz/tart/`${TS_HOSTNAME}`/api/v1/
- `${LOGIN_PW}` is used to log in to the TART web interface
- `${SECRET_KEY}` is used to secure the JWT token used for authentication


#### Modify default antenna positions

Create a directory for the telescope configuration:
```bash
    mkdir -p ~/telescope_config
```
Change the default antenna positions to be the ones for your TART.
```bash
    telescope_config.json
    calibrated_antenna_positions.json
```
Now copy docker-compose-telescope.yml -> compose.yml
```bash
    docker compose up -d
```
This will download and launch all the necessary processes in docker containers on the pi.

### Step 3.

To make the system start automatically at startup (and run in the background) modify the line in step 3 to

    docker compose up -d


### Testing

Point your browser to the raspberry pi (https://api.elec.ac.nz/tart/${TS_HOSTNAME}/home). You should see the telescope web interface.

On a different computer, you should be able to download data from the command line using the web api.

    sudo pip3 install tart_tools
    tart_download_data --api http://tart2-dev.local --pw <passwd> --raw

This should download some HDF files to your local machine. These can be checked using the HDFCompass programme (apt install hdf-compass)


#### Documentation Server

Point your browser at  [https://api.elec.ac.nz/tart/${TS_HOSTNAME}/doc](https://api.elec.ac.nz/tart/${TS_HOSTNAME}/doc/). You should see the documentation for the TART web API.

#### Live Telescope View

Point your browser at the target Pi [http:/my-pi-name/](http:/tart2-dev.local/). You should see the TART web interface. Remember to login and change the mode to 'vis' so that the telescope starts acquiring data.


## Calibration

The calibration software is also packaged with docker, and should run on a reasonably fast machine with access to the radio telescope. It uses the object position server to get a catalog of known objects that should be in the telescope field of view, and calculates gains and phases based on this information. See the [containers/calibration_server](containers/calibration_server/README.md) directory.

## Object Position Server

The object position server runs on a host, and provides a list of known objects for any location on earth and any time. A public server is available at https://tart.elec.ac.nz/catalog. The default installation of the operating software uses this server. You can test it using

    https://tart.elec.ac.nz/catalog/catalog?date=2019-02-07T09:13:28+13:00&lat=-45.85177&lon=170.5456

If you wish to install your own server, you can build the docker container in the [containers/object_position_server](containers/object_position_server/README.md) directory.
