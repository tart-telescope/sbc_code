#!/bin/sh
#
# Install the sbc code on a client single board computer

sudo apt update
sudo apt dist-upgrade
sudo apt install tmux

curl -fsSL https://tailscale.com/install.sh | sh

for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker $USER

mkdir -p ~/telescope_config


# Create .env file next to the docker-compose-telescope.yml
echo "TS_HOSTNAME='MyNewTelescope'" > .env
echo "LOGIN_PW='somethingSecret'" >> .env
echo "SECRET_KEY='anotherSecretUsedForToken'" >> .env
# Copy calibrated_antenna_positions.json to ~/telescope_config/calibrated_antenna_positions.json
cp calibrated_antenna_positions.json ~/telescope_config/calibrated_antenna_positions.json
# Edit and copy telescope_config.json to ~/telescope_config/telescope_config.json
cp telescope_config.json ~/telescope_config/telescope_config.json

echo "    sudo raspi-config -- enable SPI" 
sudo reboot

#Now set up tailscale onto the elec.ac.nz tailcale network. This is done using

echo "After Reboot, do the following:"
echo "    sudo tailscale up"
